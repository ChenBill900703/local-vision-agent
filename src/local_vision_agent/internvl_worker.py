"""One pinned offline InternVL load, explicit CUDA placement, bounded development queries."""

import argparse
import gc
import importlib
import json
import os
import sys
import time
import traceback
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .capability_gate import OPERATIONS, ExecutionReceipt
from .gpu_guard import GpuGuard, GpuPolicy, ModelMemorySpec
from .internvl_policy import CORE, PROBES, probe_gate, validate_assets
from .pilot_cleanup import clear_workspaces
from .pilot_policy import PilotBudget, PilotLimits, PilotRefusal, validate_image
from .pilot_worker import Evidence, deny_network, inspect_placement, measure


def tensor_record(value: Any) -> dict[str, Any]:
    if str(value.device) != "cuda:0":
        raise PilotRefusal("NON_CUDA_COMPUTE_OR_CACHE")
    return {"device": str(value.device), "dtype": str(value.dtype), "shape": list(value.shape)}


def model_session(
    root: Path,
    torch: Any,
    evidence: Evidence,
    guard: GpuGuard,
    limits: PilotLimits,
    cold_start: float,
    *,
    capability: bool = False,
) -> None:
    """All model/tensor references stay in this frame, released before cleanup."""
    sys.path.insert(0, str(root / "controlled"))
    config_type = importlib.import_module(
        "iv3_fixed.configuration_internvl_chat"
    ).InternVLChatConfig
    model_type = importlib.import_module("iv3_fixed.modeling_internvl_chat").InternVLChatModel
    conversation = importlib.import_module("iv3_fixed.conversation").get_conv_template
    from safetensors import safe_open
    from transformers import AutoTokenizer, GenerationConfig
    from transformers.modeling_utils import no_init_weights

    assets = root / "upstream/instruct"
    config = config_type(**json.loads((assets / "config.json").read_text(encoding="utf8")))
    if config.vision_config.drop_path_rate != 0 or config.force_image_size != 448:
        raise PilotRefusal("UNREVIEWED_VISION_CONFIGURATION")
    config.vision_config.use_flash_attn = False
    old_dtype = torch.get_default_dtype()
    try:
        torch.set_default_dtype(torch.bfloat16)
        with torch.device("cuda:0"), torch.inference_mode(), no_init_weights():
            model = model_type(config, use_flash_attn=False)
            with safe_open(str(assets / "model.safetensors"), framework="pt", device=0) as weights:
                targets = dict(model.named_parameters())
                if set(targets) != set(weights.keys()):
                    raise PilotRefusal("WEIGHT_KEYS_MISMATCH")
                for name, target in targets.items():
                    tensor = weights.get_tensor(name)
                    if tensor.dtype != torch.bfloat16 or target.dtype != torch.bfloat16:
                        raise PilotRefusal("WEIGHT_PRECISION")
                    if tensor.shape != target.shape or str(tensor.device) != "cuda:0":
                        raise PilotRefusal("WEIGHT_SHAPE_OR_DEVICE")
                    target.copy_(tensor)
                    del tensor
                del target, targets
            model.eval().requires_grad_(False)
    finally:
        torch.set_default_dtype(old_dtype)
    tokenizer = AutoTokenizer.from_pretrained(
        str(assets),
        local_files_only=True,  # type: ignore[no-untyped-call]
        trust_remote_code=False,
        use_fast=True,
    )
    model.img_context_token_id = tokenizer.convert_tokens_to_ids("<IMG_CONTEXT>")
    if model.num_image_token != 256:
        raise PilotRefusal("IMAGE_TOKEN_COUNT")
    torch.cuda.synchronize(0)
    elapsed = time.monotonic() - cold_start
    evidence.emit(
        "model_loaded",
        cold_load_s=elapsed,
        placement=inspect_placement(torch, model),
        measurement=measure(torch, guard),
        attention="eager",
        precision="bfloat16",
    )
    if elapsed > limits.load_s:
        raise PilotRefusal("LOAD_TIMEOUT")
    manifest = json.loads((root / "evidence/development_manifest.json").read_text(encoding="utf8"))
    if len(manifest["images"]) != 1 or manifest["images"][0]["id"] != "synthetic-shapes-v1":
        raise PilotRefusal("ORIGINAL_FIXTURE_REQUIRED")
    item = manifest["images"][0]
    budget = PilotBudget(limits)
    budget.start_image()
    evidence.emit("image_start", input_id=item["id"])
    start = time.monotonic()
    path = Path(item["path"])
    validate_image(path, item["sha256"], limits)
    import numpy as np
    from PIL import Image, ImageOps

    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        resized = image.resize((448, 448), Image.Resampling.BICUBIC)
        array: Any = np.asarray(resized, dtype=np.float32) / 255.0
        array = (array - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array(
            [0.229, 0.224, 0.225], dtype=np.float32
        )
        pixels = (
            torch.from_numpy(array.transpose(2, 0, 1).copy())
            .unsqueeze(0)
            .to(device="cuda:0", dtype=torch.bfloat16)
        )
        image.close()
        resized.close()
    torch.cuda.synchronize(0)
    evidence.emit(
        "image_ready",
        latency_s=time.monotonic() - start,
        tile_count=1,
        placement=tensor_record(pixels),
        measurement=measure(torch, guard),
    )
    answers: dict[str, str] = {}
    operations = list(OPERATIONS if capability else CORE)
    for index in range(len(OPERATIONS) if capability else 8):
        if index == 4 and not capability:
            passed = probe_gate(answers)
            evidence.emit(
                "probe_gate",
                passed=passed,
                policy="conservative-fixture-lexical-v1",
                reason="fixed caption claim supported"
                if passed
                else "core answers not all accepted; no extra queries",
            )
            if not passed:
                break
            operations.extend(PROBES)
        operation, question = operations[index]
        template = conversation(model.template)
        template.system_message = model.system_message
        template.append_message(template.roles[0], "<image>\n" + question)
        template.append_message(template.roles[1], None)
        prompt = template.get_prompt().replace(
            "<image>", "<img>" + "<IMG_CONTEXT>" * 256 + "</img>", 1
        )
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to("cuda:0")
        attention_mask = inputs["attention_mask"].to("cuda:0")
        count = int(input_ids.shape[1])
        budget.before_call(count, 128)
        eos = tokenizer.convert_tokens_to_ids(template.sep.strip())
        settings = {
            "do_sample": False,
            "temperature": 0.0,
            "num_beams": 1,
            "max_new_tokens": 128,
            "eos_token_id": eos,
            "pad_token_id": tokenizer.pad_token_id,
            "return_dict_in_generate": True,
            "output_scores": False,
            "use_cache": True,
        }
        generation = GenerationConfig(**settings)  # type: ignore[no-untyped-call]
        evidence.emit(
            "call_start",
            operation=operation,
            prompt=question,
            rendered_prompt=prompt,
            input_token_ids=input_ids[0].tolist(),
            input_tokens=count,
            generation_config=generation.to_dict(),
            placement={
                "input_ids": tensor_record(input_ids),
                "attention_mask": tensor_record(attention_mask),
            },
        )
        torch.cuda.synchronize(0)
        start = time.monotonic()
        with torch.inference_mode():
            visual = model.extract_feature(pixels)
            torch.cuda.synchronize(0)
            visual_seconds = time.monotonic() - start
            evidence.emit(
                "visual_done",
                operation=operation,
                latency_s=visual_seconds,
                placement=tensor_record(visual),
                measurement=measure(torch, guard),
            )
            generation_start = time.monotonic()
            output = model.generate(
                pixel_values=pixels,
                visual_features=visual,
                input_ids=input_ids,
                attention_mask=attention_mask,
                generation_config=generation,
            )
            torch.cuda.synchronize(0)
            generation_seconds = time.monotonic() - generation_start
        elapsed = time.monotonic() - start
        ids = output.sequences[0].tolist()
        budget.after_call(len(ids))
        raw = tokenizer.decode(ids, skip_special_tokens=True)
        decoded_with_special = tokenizer.decode(ids, skip_special_tokens=False)
        cache = output.past_key_values
        if cache is None or not hasattr(cache, "layers") or len(cache.layers) != 28:
            raise PilotRefusal("KV_CACHE_NOT_OBSERVABLE")
        cache_records = []
        for layer in cache.layers:
            for value in (layer.keys, layer.values):
                if value.shape[-2] > count + 128:
                    raise PilotRefusal("CACHE_LENGTH")
                cache_records.append(tensor_record(value))
        answers[operation] = raw
        measurement = measure(torch, guard)
        receipt = ExecutionReceipt(
            response=raw,
            decoded=True,
            worker_healthy=True,
            transport="completed",
            error=None,
            input_tokens=count,
            output_tokens=len(ids),
            image_output_tokens=budget.output_tokens,
            calls=budget.calls,
            image_calls=budget.image_calls,
            images=budget.images,
            elapsed_s=time.monotonic() - start,
            image_elapsed_s=time.monotonic() - budget.image_started,
            session_elapsed_s=time.monotonic() - cold_start,
            reserved_mib=measurement["reserved_bytes"] / 1048576,
            free_mib=min(
                measurement["cuda_free_bytes"] / 1048576, measurement["nvidia"]["free_mib"]
            ),
        )
        # Persist the raw response even if the engineering gate subsequently refuses it.
        evidence.emit(
            "call_done",
            operation=operation,
            raw_response=raw,
            raw_with_special_tokens=decoded_with_special,
            output_token_ids=ids,
            input_tokens=count,
            output_tokens=len(ids),
            latency_s=elapsed,
            visual_s=visual_seconds,
            generation_s=generation_seconds,
            kv_placement=cache_records,
            measurement=measurement,
            execution_receipt=asdict(receipt),
            worker_status="healthy",
            stop_reason="eos"
            if ids and ids[-1] == eos
            else "token_limit"
            if len(ids) == 128
            else "generation_stopped",
        )
        if capability:
            receipt.validate(limits)
        del cache, layer, value, output, visual, input_ids, attention_mask, inputs
        if elapsed > limits.call_s:
            raise PilotRefusal("CALL_TIMEOUT")
    evidence.emit(
        "pilot_complete",
        total_calls=budget.calls,
        model_load_count=1,
        offline_mode=True,
        placement=inspect_placement(torch, model),
    )


def run(root: Path, run_dir: Path, *, capability: bool = False) -> int:
    limits = PilotLimits()
    evidence = Evidence(run_dir, pipe=True)
    evidence.emit("load_start", limits=asdict(limits))
    start = time.monotonic()
    torch: Any = None
    exit_code = 1
    try:
        validate_assets(root, Path(__file__).resolve().parents[2])
        deny_network(evidence)
        guard = GpuGuard(GpuPolicy(limits.ceiling_mib, limits.reserve_mib))
        before = guard.preflight(
            ModelMemorySpec("InternVL3 UNMEASURED PILOT VRAM ESTIMATE", 6000),
            load_options={"device_map": {"": "cuda:0"}},
        )
        if before.name != "NVIDIA GeForce RTX 3070 Ti":
            raise PilotRefusal("WRONG_GPU")
        evidence.emit("preflight_pass", snapshot=asdict(before), estimate_mib=6000)
        import torch as torch_module

        torch = torch_module
        torch.cuda.init()
        if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
            raise PilotRefusal("CUDA_DEVICE_MISMATCH")
        free, total = torch.cuda.mem_get_info(0)
        context_mib = max(0, before.free_mib - free / 1048576)
        if context_mib > 1007 or free / 1048576 < 6000 - context_mib + 1536:
            raise PilotRefusal("POST_INIT_BUDGET")
        torch.cuda.set_per_process_memory_fraction(5400 * 1048576 / total, 0)
        torch.manual_seed(0)
        torch.cuda.reset_peak_memory_stats(0)
        evidence.emit(
            "cuda_baseline",
            context_mib=context_mib,
            torch_version=torch.__version__,
            cuda_version=torch.version.cuda,
            is_available=torch.cuda.is_available(),
            measurement=measure(torch, guard),
        )
        model_session(root, torch, evidence, guard, limits, start, capability=capability)
        exit_code = 0
    except Exception as exc:  # noqa: BLE001 -- process boundary retains errors without retries
        evidence.emit(
            "failure",
            exception=type(exc).__name__,
            message=str(exc),
            traceback=traceback.format_exc(),
        )
    finally:
        evidence.emit("cleanup_start")
        start = time.monotonic()
        gc.collect()
        if torch is not None and torch.cuda.is_initialized():
            try:
                evidence.emit(
                    "before_cleanup", measurement=measure(torch, GpuGuard(), enforce=False)
                )
                evidence.emit("workspace_cleanup", **clear_workspaces(torch))
                measurement = measure(torch, GpuGuard(), enforce=False)
                empty = measurement["allocated_bytes"] == measurement["reserved_bytes"] == 0
                if not empty:
                    exit_code = 1
                evidence.emit(
                    "cleanup_done",
                    latency_s=time.monotonic() - start,
                    allocator_empty=empty,
                    measurement=measurement,
                )
            except Exception as exc:  # noqa: BLE001 -- preserve failure and exit process
                exit_code = 1
                evidence.emit("cleanup_failure", message=str(exc), traceback=traceback.format_exc())
        evidence.emit("worker_done", exit_code=exit_code)
    return exit_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--capability", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps({"phase": "ready", "pid": os.getpid(), "monotonic": time.monotonic()}),
        flush=True,
    )
    if sys.stdin.readline().strip() != "GO":
        raise SystemExit("SUPERVISOR_HANDSHAKE_REQUIRED")
    raise SystemExit(run(args.root.resolve(), args.run_dir.resolve(), capability=args.capability))
