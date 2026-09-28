"""Private pinned CUDA implementation. Only the supervised worker may instantiate it."""

import gc
import importlib
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .contracts import AgentError, ImageInfo, ImageInput, Request
from .gpu_guard import GpuGuard, GpuPolicy, ModelMemorySpec
from .image_input import inspect_image
from .internvl_contract import (
    RuntimeConfig,
    preprocess_array,
    validate_environment,
    validate_request,
)
from .internvl_policy import REVISION, validate_assets
from .internvl_worker import tensor_record
from .pilot_cleanup import clear_workspaces
from .pilot_worker import Evidence, deny_network, inspect_placement, measure


class InternVLBackend:
    def __init__(self, root: Path, config: RuntimeConfig, evidence: Evidence) -> None:
        self.root, self.config, self.evidence = root, config, evidence
        self.torch: Any = None
        self.model: Any = None
        self.tokenizer: Any = None
        self.pixels: Any = None
        self.conversation: Any = None
        self.image: ImageInfo | None = None
        self.calls = self.output_tokens = 0
        self.started = self.image_started = 0.0
        self.guard = GpuGuard(GpuPolicy(6400, 1536))
        self.loaded_once = False

    def load(self) -> dict[str, Any]:
        if self.loaded_once:
            raise AgentError("MODEL_RELOAD_FORBIDDEN")
        self.loaded_once = True
        self.started = time.monotonic()
        self.evidence.emit("load_start")
        versions = validate_environment()
        validate_assets(self.root, Path(__file__).resolve().parents[2])
        deny_network(self.evidence)
        before = self.guard.preflight(
            ModelMemorySpec("InternVL bounded development estimate", 6000),
            load_options={"device_map": {"": "cuda:0"}},
        )
        if before.name != "NVIDIA GeForce RTX 3070 Ti":
            raise AgentError("WRONG_GPU")
        self.evidence.emit("preflight_pass", snapshot=asdict(before))
        import torch

        self.torch = torch
        torch.cuda.init()  # type: ignore[no-untyped-call]
        if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
            raise AgentError("CUDA_DEVICE_MISMATCH")
        free, total = torch.cuda.mem_get_info(0)
        context = max(0, before.free_mib - free / 1048576)
        if context > 1007 or free / 1048576 < 6000 - context + 1536:
            raise AgentError("POST_INIT_BUDGET")
        torch.cuda.set_per_process_memory_fraction(5400 * 1048576 / total, 0)
        torch.manual_seed(0)
        torch.cuda.reset_peak_memory_stats(0)
        self.evidence.emit("cuda_baseline", measurement=measure(torch, self.guard))
        sys.path.insert(0, str(self.root / "controlled"))
        config_type = importlib.import_module(
            "iv3_fixed.configuration_internvl_chat"
        ).InternVLChatConfig
        model_type = importlib.import_module("iv3_fixed.modeling_internvl_chat").InternVLChatModel
        self.conversation = importlib.import_module("iv3_fixed.conversation").get_conv_template
        from safetensors import safe_open
        from transformers import AutoTokenizer
        from transformers.modeling_utils import no_init_weights

        assets = self.root / "upstream/instruct"
        model_config = config_type(
            **json.loads((assets / "config.json").read_text(encoding="utf8"))
        )
        if model_config.vision_config.drop_path_rate != 0 or model_config.force_image_size != 448:
            raise AgentError("UNREVIEWED_VISION_CONFIGURATION")
        model_config.vision_config.use_flash_attn = False
        original_dtype = torch.get_default_dtype()
        try:
            torch.set_default_dtype(torch.bfloat16)
            with torch.device("cuda:0"), torch.inference_mode(), no_init_weights():
                self.model = model_type(model_config, use_flash_attn=False)
                with safe_open(
                    str(assets / "model.safetensors"), framework="pt", device=0
                ) as weights:
                    targets = dict(self.model.named_parameters())
                    if set(targets) != set(weights.keys()):
                        raise AgentError("WEIGHT_KEYS_MISMATCH")
                    for name, target in targets.items():
                        tensor = weights.get_tensor(name)
                        if (
                            tensor.dtype != torch.bfloat16
                            or target.dtype != torch.bfloat16
                            or tensor.shape != target.shape
                            or str(tensor.device) != "cuda:0"
                        ):
                            raise AgentError("WEIGHT_DTYPE_SHAPE_OR_DEVICE")
                        target.copy_(tensor)
                        del tensor
                    del target, targets
                self.model.eval().requires_grad_(False)
        finally:
            torch.set_default_dtype(original_dtype)
        self.tokenizer = AutoTokenizer.from_pretrained(
            str(assets), local_files_only=True, trust_remote_code=False, use_fast=True
        )  # type: ignore[no-untyped-call]
        self.model.img_context_token_id = self.tokenizer.convert_tokens_to_ids("<IMG_CONTEXT>")
        if self.model.num_image_token != 256:
            raise AgentError("IMAGE_TOKEN_COUNT")
        torch.cuda.synchronize(0)
        metadata = {
            "dependencies": versions,
            "model_id": "OpenGVLab/InternVL3-2B-Instruct",
            "revision": REVISION,
            "load_seconds": time.monotonic() - self.started,
            "precision": "bfloat16",
            "device": "cuda:0",
            "attention": "eager",
            "offline": True,
            "preprocessing": self.config.preprocessing,
            "placement": inspect_placement(torch, self.model),
            "measurement": measure(torch, self.guard),
        }
        if metadata["load_seconds"] > self.config.load_timeout_s:  # type: ignore[operator]
            raise AgentError("LOAD_TIMEOUT")
        self.evidence.emit("model_loaded", **metadata)
        return metadata

    def begin_image(self, item: ImageInput, expected_hash: str) -> dict[str, Any]:
        if self.model is None or self.image is not None:
            raise AgentError("ONE_IMAGE_PER_WORKER")
        self.image_started = time.monotonic()
        self.image = inspect_image(item, self.config.limits)
        if self.image.sha256 != expected_hash:
            raise AgentError("IMAGE_CHANGED")
        self.evidence.emit("image_start", input_id=item.input_id, image=asdict(self.image))
        array = preprocess_array(item.path, expected_hash, self.config.limits.max_input_bytes)
        self.pixels = (
            self.torch.from_numpy(array).unsqueeze(0).to(device="cuda:0", dtype=self.torch.bfloat16)
        )
        self.torch.cuda.synchronize(0)
        data = {
            "image": asdict(self.image),
            "tile_count": 1,
            "preprocessing": self.config.preprocessing,
            "latency_s": time.monotonic() - self.image_started,
            "placement": tensor_record(self.pixels),
            "measurement": measure(self.torch, self.guard),
        }
        self.evidence.emit("image_ready", **data)
        return data

    def invoke(self, request: Request) -> dict[str, Any]:
        validate_request(request, self.config.limits)
        if self.model is None or self.image is None:
            raise AgentError("MODEL_OR_IMAGE_NOT_READY")
        limits = self.config.limits
        if time.monotonic() - self.image_started >= limits.per_image_timeout_s:
            raise AgentError("IMAGE_TIMEOUT")
        if time.monotonic() - self.started >= self.config.session_timeout_s:
            raise AgentError("SESSION_TIMEOUT")
        if self.calls >= min(limits.max_model_calls, limits.max_tool_calls, limits.max_iterations):
            raise AgentError("MODEL_CALL_LIMIT")
        if self.output_tokens + request.max_output_tokens > limits.max_total_output_tokens:
            raise AgentError("OUTPUT_LIMIT")
        template = self.conversation(self.model.template)
        template.system_message = self.model.system_message
        template.append_message(template.roles[0], "<image>\n" + request.prompt)
        template.append_message(template.roles[1], None)
        prompt = template.get_prompt().replace(
            "<image>", "<img>" + "<IMG_CONTEXT>" * 256 + "</img>", 1
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to("cuda:0")
        attention_mask = inputs["attention_mask"].to("cuda:0")
        count = int(input_ids.shape[1])
        if count > limits.max_input_tokens:
            raise AgentError("INPUT_TOKEN_LIMIT")
        self.calls += 1
        from transformers import GenerationConfig

        eos = self.tokenizer.convert_tokens_to_ids(template.sep.strip())
        generation = GenerationConfig(
            do_sample=False,
            temperature=0.0,
            num_beams=1,
            max_new_tokens=request.max_output_tokens,
            eos_token_id=eos,
            pad_token_id=self.tokenizer.pad_token_id,
            return_dict_in_generate=True,
            output_scores=False,
            use_cache=True,
        )  # type: ignore[no-untyped-call]
        self.evidence.emit(
            "call_start",
            call_id=f"call-{self.calls}",
            request=asdict(request),
            rendered_prompt=prompt,
            input_token_ids=input_ids[0].tolist(),
            generation_config=generation.to_dict(),
            input_placement=[tensor_record(input_ids), tensor_record(attention_mask)],
        )
        self.torch.cuda.synchronize(0)
        start = time.monotonic()
        with self.torch.inference_mode():
            visual = self.model.extract_feature(self.pixels)
            self.torch.cuda.synchronize(0)
            visual_s = time.monotonic() - start
            self.evidence.emit(
                "visual_done",
                latency_s=visual_s,
                placement=tensor_record(visual),
                measurement=measure(self.torch, self.guard),
            )
            generation_start = time.monotonic()
            output = self.model.generate(
                pixel_values=self.pixels,
                visual_features=visual,
                input_ids=input_ids,
                attention_mask=attention_mask,
                generation_config=generation,
            )
            self.torch.cuda.synchronize(0)
            generation_s = time.monotonic() - generation_start
        elapsed = time.monotonic() - start
        ids = output.sequences[0].tolist()
        raw = self.tokenizer.decode(ids, skip_special_tokens=True)
        cache = output.past_key_values
        if cache is None or not hasattr(cache, "layers") or len(cache.layers) != 28:
            raise AgentError("KV_CACHE_NOT_OBSERVABLE")
        placements = []
        for layer in cache.layers:
            for value in (layer.keys, layer.values):
                if value.shape[-2] > count + request.max_output_tokens:
                    raise AgentError("CACHE_LENGTH")
                placements.append(tensor_record(value))
        self.output_tokens += len(ids)
        result = {
            "raw_response": raw,
            "output_tokens": len(ids),
            "input_tokens": count,
            "output_token_ids": ids,
            "raw_with_special_tokens": self.tokenizer.decode(ids, skip_special_tokens=False),
            "latency_s": elapsed,
            "visual_s": visual_s,
            "generation_s": generation_s,
            "measurement": measure(self.torch, self.guard),
            "kv_placement": placements,
            "stop_reason": "eos" if ids and ids[-1] == eos else "token_limit",
            "call_id": f"call-{self.calls}",
            "worker_status": "healthy",
        }
        self.evidence.emit("call_done", **result)
        if (
            not isinstance(raw, str)
            or not raw.strip()
            or "\ufffd" in raw
            or not 0 < len(ids) <= request.max_output_tokens
        ):
            raise AgentError("INVALID_TOOL_RESULT")
        raw.encode("utf8", errors="strict")
        if elapsed >= limits.per_call_timeout_s:
            raise AgentError("TOOL_TIMEOUT")
        return result

    def unload(self) -> dict[str, Any]:
        self.evidence.emit("cleanup_start")
        start = time.monotonic()
        self.model = self.tokenizer = self.pixels = self.conversation = None
        self.image = None
        gc.collect()
        measurement: dict[str, Any] = {"allocated_bytes": 0, "reserved_bytes": 0}
        if self.torch is not None and self.torch.cuda.is_initialized():
            self.evidence.emit("workspace_cleanup", **clear_workspaces(self.torch))
            measurement = measure(self.torch, self.guard, enforce=False)
        result = {"measurement": measurement, "latency_s": time.monotonic() - start}
        self.evidence.emit("cleanup_done", **result)
        if measurement["allocated_bytes"] != 0 or measurement["reserved_bytes"] != 0:
            raise AgentError("CLEANUP_FAILED")
        return result
