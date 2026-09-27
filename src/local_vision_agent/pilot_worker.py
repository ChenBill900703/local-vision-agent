"""Single persistent, offline CUDA model worker for ONE authorized exploratory pilot.

All heavyweight imports occur after real GpuGuard.preflight. No automatic retries.
Parent supervisor enforces hard operation/image/session deadlines by process exit.
"""

import argparse
import gc
import importlib
import json
import os
import sys
import time
import traceback
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .gpu_guard import GpuGuard, GpuPolicy, ModelMemorySpec, query_gpu_snapshot
from .language_diagnostic import OPERATIONS
from .pilot_cleanup import clear_workspaces
from .pilot_policy import (
    LABEL,
    PilotBudget,
    PilotLimits,
    PilotRefusal,
    validate_assets,
    validate_image,
)


class Evidence:
    def __init__(self, directory: Path, *, pipe: bool = False) -> None:
        self.directory = directory
        self.events = directory / "events.jsonl"
        self.pipe = pipe

    def emit(self, phase: str, **values: Any) -> None:
        record = {
            "label": LABEL,
            "phase": phase,
            "pid": os.getpid(),
            "time": datetime.now().astimezone().isoformat(),
            "monotonic": time.monotonic(),
            **values,
        }
        line = json.dumps(record, ensure_ascii=False, allow_nan=False)
        with self.events.open("a", encoding="utf8") as handle:
            handle.write(line + "\n")
            handle.flush()
        if self.pipe:
            print(line, flush=True)


def deny_network(evidence: Evidence) -> None:
    os.environ.update(
        HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1", DO_NOT_TRACK="1"
    )

    def audit(event: str, args: tuple[Any, ...]) -> None:
        if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto"}:
            evidence.emit("network_violation", event=event)
            raise PilotRefusal("OFFLINE_NETWORK_ATTEMPT")

    sys.addaudithook(audit)


def measure(torch: Any, guard: GpuGuard, *, enforce: bool = True) -> dict[str, Any]:
    torch.cuda.synchronize(0)
    snapshot = query_gpu_snapshot(0)
    free, total = torch.cuda.mem_get_info(0)
    allocated, reserved = torch.cuda.memory_allocated(0), torch.cuda.memory_reserved(0)
    values = {
        "nvidia": asdict(snapshot),
        "cuda_free_bytes": free,
        "cuda_total_bytes": total,
        "allocated_bytes": allocated,
        "reserved_bytes": reserved,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(0),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(0),
    }
    if enforce:
        guard.assert_runtime_reserved((reserved + 1048575) // 1048576)
        if min(snapshot.free_mib * 1048576, free) < 1536 * 1048576:
            raise PilotRefusal("FREE_RESERVE_VIOLATION:" + json.dumps(values))
    return values


def inspect_placement(torch: Any, model: Any, encoded: Any = None) -> dict[str, Any]:
    tensors = [("parameter:" + n, t) for n, t in model.named_parameters()]
    tensors += [("buffer:" + n, t) for n, t in model.named_buffers()]
    if encoded is not None:
        tensors += [
            (f"encoded:{i}:{j}", t)
            for i, pair in enumerate(encoded.caches)
            for j, t in enumerate(pair)
        ]
    details = [
        {
            "name": name,
            "device": str(t.device),
            "dtype": str(t.dtype),
            "shape": list(t.shape),
            "bytes": t.numel() * t.element_size(),
        }
        for name, t in tensors
    ]
    bad = [d for d in details if d["device"] != "cuda:0"]
    if bad:
        raise PilotRefusal("NON_CUDA_MODEL_STATE:" + json.dumps(bad))
    return {"all_cuda0": True, "tensors": details}


def run(
    root: Path,
    run_dir: Path,
    *,
    repair: bool = False,
    pipe: bool = False,
    final_language: bool = False,
) -> int:
    if repair and final_language:
        raise PilotRefusal("CONFLICTING_PILOT_MODES")
    limits = PilotLimits()
    evidence = Evidence(run_dir, pipe=pipe)
    evidence.emit("load_start", limits=asdict(limits))
    cold_start = time.monotonic()
    model: Any = None
    encoded: Any = None
    torch: Any = None
    exit_code = 1
    try:
        validate_assets(root, repair=repair)
        deny_network(evidence)
        guard = GpuGuard(GpuPolicy(limits.ceiling_mib, limits.reserve_mib))
        before = guard.preflight(
            ModelMemorySpec("Moondream2 UNMEASURED PILOT ESTIMATE", limits.estimated_peak_mib),
            load_options={"device_map": {"": "cuda:0"}},
        )
        if before.name != "NVIDIA GeForce RTX 3070 Ti":
            raise PilotRefusal("WRONG_GPU")
        evidence.emit(
            "preflight_pass",
            snapshot=asdict(before),
            estimate_label="UNMEASURED PILOT ESTIMATE",
            estimated_mib=6000,
        )
        import torch as torch_module

        torch = torch_module
        torch.cuda.init()
        if torch.cuda.device_count() != 1 or torch.cuda.get_device_name(0) != before.name:
            raise PilotRefusal("CUDA_DEVICE_MISMATCH")
        free, total = torch.cuda.mem_get_info(0)
        context_used_mib = max(0, before.free_mib - free / 1048576)
        if context_used_mib > 891:
            raise PilotRefusal("CONTEXT_EXCEEDS_PROVISIONAL_ALLOWANCE")
        remaining_estimate = limits.estimated_peak_mib - context_used_mib
        if free / 1048576 < remaining_estimate + limits.reserve_mib:
            raise PilotRefusal("POST_INIT_FREE_INSUFFICIENT")
        torch.cuda.set_per_process_memory_fraction(limits.allocator_cap_mib * 1048576 / total, 0)
        torch.manual_seed(0)
        torch.cuda.reset_peak_memory_stats(0)
        evidence.emit(
            "cuda_baseline",
            torch_version=torch.__version__,
            cuda_version=torch.version.cuda,
            is_available=torch.cuda.is_available(),
            devices=torch.cuda.device_count(),
            context_used_mib=context_used_mib,
            measurement=measure(torch, guard),
        )
        sys.path.insert(0, str(root / ("controlled-repair1" if repair else "controlled")))
        # Review-approved local immutable hash-checked source, never trust floating remote code.
        config_module = importlib.import_module("md2_fixed.config")
        core_module = importlib.import_module("md2_fixed.moondream")
        from safetensors import safe_open

        with torch.device("cuda:0"), torch.inference_mode():
            model = core_module.MoondreamModel(config_module.MoondreamConfig(), setup_caches=False)
            with safe_open(
                str(root / "upstream/model/model.safetensors"), framework="pt", device=0
            ) as weights:
                targets = dict(model.named_parameters())
                expected = {"model." + name for name in targets}
                if set(weights.keys()) != expected:
                    raise PilotRefusal("WEIGHT_KEY_MISMATCH")
                for name, target in targets.items():
                    tensor = weights.get_tensor("model." + name)
                    if tensor.dtype != torch.bfloat16 or tensor.device.type != "cuda":
                        raise PilotRefusal("WEIGHT_DTYPE_OR_DEVICE")
                    if tensor.shape != target.shape:
                        raise PilotRefusal("WEIGHT_SHAPE")
                    target.copy_(tensor)
                    del tensor
                del targets, target
            model.eval().requires_grad_(False)
            model._setup_caches()
        torch.cuda.synchronize(0)
        load_seconds = time.monotonic() - cold_start
        evidence.emit(
            "model_loaded",
            cold_load_s=load_seconds,
            measurement=measure(torch, guard),
            placement=inspect_placement(torch, model),
        )
        if load_seconds > limits.load_s:
            raise PilotRefusal("LOAD_TIMEOUT")
        # Record actual tensors arriving at vision and text compute, not just model.device.
        input_records = []
        original_vision, original_prefill = model._vis_enc, model._prefill
        original_decode = model._decode_one_tok

        def vision_checked(x: Any) -> Any:
            if x.device != torch.device("cuda:0") or x.shape[0] > 5:
                raise PilotRefusal("VISION_INPUT_DEVICE_OR_CROPS")
            input_records.append(
                {"kind": "vision", "device": str(x.device), "shape": list(x.shape)}
            )
            return original_vision(x)

        def prefill_checked(x: Any, mask: Any, positions: Any, lora: Any) -> Any:
            for tensor in (x, mask, positions):
                if tensor.device != torch.device("cuda:0"):
                    raise PilotRefusal("PREFILL_INPUT_DEVICE")
            input_records.append(
                {
                    "kind": "prefill",
                    "device": str(x.device),
                    "shape": list(x.shape),
                    "positions_device": str(positions.device),
                }
            )
            return original_prefill(x, mask, positions, lora)

        def decode_checked(x: Any, mask: Any, positions: Any, lora: Any) -> Any:
            for tensor in (x, mask, positions):
                if tensor.device != torch.device("cuda:0"):
                    raise PilotRefusal("DECODE_INPUT_DEVICE")
            if not any(r["kind"] == "decode" for r in input_records):
                input_records.append(
                    {
                        "kind": "decode",
                        "device": str(x.device),
                        "shape": list(x.shape),
                        "positions_device": str(positions.device),
                    }
                )
            return original_decode(x, mask, positions, lora)

        model._vis_enc, model._prefill = vision_checked, prefill_checked
        model._decode_one_tok = decode_checked
        manifest = json.loads((root / "evidence/development_manifest.json").read_text())
        if final_language and (
            len(manifest["images"]) != 1 or manifest["images"][0]["id"] != "synthetic-shapes-v1"
        ):
            raise PilotRefusal("FINAL_DIAGNOSTIC_REQUIRES_ORIGINAL_SINGLE_FIXTURE")
        if not 1 <= len(manifest["images"]) <= limits.max_images:
            raise PilotRefusal("IMAGE_COUNT")
        budget = PilotBudget(limits)
        settings = {"max_tokens": 128, "temperature": 0.0, "top_p": 1.0}
        question = "請只用繁體中文回答：圖片中有哪些形狀？它們各是什麼顏色？"
        from PIL import Image, ImageOps

        for item in manifest["images"]:
            budget.start_image()
            image_start = budget.image_started
            evidence.emit("image_start", input_id=item["id"], image_started=image_start)
            path = Path(item["path"])
            validate_image(path, item["sha256"], limits)
            with Image.open(path) as opened:
                image = ImageOps.exif_transpose(opened).convert("RGB")
            budget.before_call()
            evidence.emit("call_start", operation="encode", image_started=image_start)
            torch.cuda.synchronize(0)
            torch.cuda.reset_peak_memory_stats(0)
            start = time.monotonic()
            with torch.device("cuda:0"), torch.inference_mode():
                encoded = model.encode_image(image)
            torch.cuda.synchronize(0)
            elapsed = time.monotonic() - start
            image.close()
            evidence.emit(
                "call_done",
                operation="encode",
                latency_s=elapsed,
                image_started=image_start,
                measurement=measure(torch, guard),
                placement=inspect_placement(torch, model, encoded),
            )
            operations = (
                (
                    ("caption_first", question, True),
                    ("caption_warm", question, True),
                    ("query_original_en", "What shapes and colors are in the image?", True),
                    ("query_original_zh", question, True),
                    ("query_single_suffix_en", "What shapes and colors are in the image?", False),
                    ("query_single_suffix_zh", question, False),
                )
                if repair
                else tuple(
                    (name, question, True)
                    for name in ("caption_first", "caption_warm", "query_first", "query_warm")
                )
            )
            if final_language:
                operations = OPERATIONS
            for operation, current_question, duplicate in operations:
                is_caption = operation.startswith("caption")
                model._pilot_duplicate_query_suffix = duplicate
                prompt_ids = (
                    model.config.tokenizer.templates["caption"]["normal"]
                    if is_caption
                    else model.config.tokenizer.templates["query"]["prefix"]
                    + model.tokenizer.encode(current_question).ids
                    + model.config.tokenizer.templates["query"]["suffix"] * (2 if duplicate else 1)
                )
                budget.before_call(len(prompt_ids), 128)
                if encoded.pos + len(prompt_ids) + 128 > model.config.text.max_context:
                    raise PilotRefusal("CONTEXT_LIMIT")
                evidence.emit(
                    "call_start",
                    operation=operation,
                    image_started=image_start,
                    prompt="caption template normal" if is_caption else current_question,
                    duplicate_suffix=duplicate,
                    prompt_token_ids=prompt_ids,
                    settings=settings,
                )
                torch.cuda.synchronize(0)
                torch.cuda.reset_peak_memory_stats(0)
                start = time.monotonic()
                with torch.device("cuda:0"), torch.inference_mode():
                    result = (
                        model.caption(encoded, length="normal", settings=settings)
                        if is_caption
                        else model.query(
                            encoded, current_question, reasoning=False, settings=settings
                        )
                    )
                torch.cuda.synchronize(0)
                elapsed = time.monotonic() - start
                token_ids = list(model._pilot_generated_token_ids)
                budget.after_call(len(token_ids))
                text = result["caption" if is_caption else "answer"]
                evidence.emit(
                    "call_done",
                    operation=operation,
                    input_id=item["id"],
                    latency_s=elapsed,
                    image_started=image_start,
                    raw_response=result,
                    input_tokens=len(prompt_ids),
                    output_tokens=len(token_ids),
                    output_token_ids=token_ids,
                    length_chars=len(text),
                    contains_cjk=any("\u4e00" <= c <= "\u9fff" for c in text),
                    malformed=not isinstance(text, str) or not text.strip(),
                    measurement=measure(torch, guard),
                    placement=inspect_placement(torch, model, encoded),
                )
                if elapsed > limits.call_s:
                    raise PilotRefusal("CALL_TIMEOUT")
            encoded = None
            if time.monotonic() - image_start > limits.image_s:
                raise PilotRefusal("IMAGE_TIMEOUT")
        evidence.emit(
            "pilot_complete",
            total_calls=budget.calls,
            compute_inputs=input_records,
            offline_mode=True,
            model_load_count=1,
        )
        exit_code = 0
    except Exception as exc:  # noqa: BLE001 -- process boundary records all failures, then cleans up
        evidence.emit(
            "failure",
            exception=type(exc).__name__,
            message=str(exc),
            traceback=traceback.format_exc(),
        )
    finally:
        evidence.emit("cleanup_start")
        start = time.monotonic()
        # Closures and bound methods also hold model references.
        encoded = model = None
        original_vision = original_prefill = vision_checked = prefill_checked = None  # type: ignore[assignment]
        original_decode = decode_checked = None  # type: ignore[assignment]
        targets = target = tensor = None  # type: ignore[assignment]  # noqa: F841
        gc.collect()
        if torch is not None and torch.cuda.is_initialized():
            if repair or final_language:
                try:
                    evidence.emit("workspace_cleanup", **clear_workspaces(torch))
                except Exception as exc:  # noqa: BLE001 -- preserve cleanup error before process exit
                    exit_code = 1
                    evidence.emit("cleanup_failure", exception=type(exc).__name__, message=str(exc))
            torch.cuda.empty_cache()
            torch.cuda.synchronize(0)
            measurement = measure(torch, GpuGuard(), enforce=False)
            if measurement["allocated_bytes"] != 0:
                exit_code = 1
            evidence.emit(
                "cleanup_done",
                latency_s=time.monotonic() - start,
                measurement=measurement,
                allocator_empty=measurement["allocated_bytes"] == 0,
            )
        evidence.emit("worker_done", exit_code=exit_code)
    return exit_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--repair1", action="store_true")
    parser.add_argument("--final-language", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps({"phase": "ready", "pid": os.getpid(), "monotonic": time.monotonic()}),
        flush=True,
    )
    if sys.stdin.readline().strip() != "GO":
        raise SystemExit("SUPERVISOR_HANDSHAKE_REQUIRED")
    raise SystemExit(
        run(
            args.root.resolve(),
            args.run_dir.resolve(),
            repair=args.repair1,
            pipe=True,
            final_language=args.final_language,
        )
    )
