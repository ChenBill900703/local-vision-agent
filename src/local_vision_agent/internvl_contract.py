"""Explicit development runtime limits, preprocessing and conservative text normalization."""

import hashlib
import importlib.metadata
import re
import tomllib
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

from .contracts import AgentError, Answer, Limits, Request
from .pilot_policy import PilotLimits
from .source_input import SourceImageLimits

PREPROCESSING = "internvl-single-tile-rgb-bicubic448-imagenet-v1"
NORMALIZER = "literal-sentence-claims-explicit-verdict-v1"

RUNTIME_VERSIONS = {
    "torch": "2.7.1+cu126",
    "torchvision": "0.22.1+cu126",
    "transformers": "4.57.6",
    "numpy": "2.4.6",
    "Pillow": "12.3.0",
    "safetensors": "0.8.0",
    "tokenizers": "0.22.2",
    "packaging": "26.3",
    "kernels": "NOT INSTALLED",
}


def validate_environment() -> dict[str, str]:
    observed = {}
    for name, expected in RUNTIME_VERSIONS.items():
        try:
            observed[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            observed[name] = "NOT INSTALLED"
        if observed[name] != expected:
            raise AgentError("DEPENDENCY_DRIFT:" + name)
    return observed


@dataclass(frozen=True)
class RuntimeConfig:
    limits: Limits
    source_image_limits: SourceImageLimits
    preprocessing: str
    load_timeout_s: float
    session_timeout_s: float

    def __post_init__(self) -> None:
        if type(self.limits) is not Limits or self.preprocessing != PREPROCESSING:
            raise AgentError("INVALID_RUNTIME_CONFIG")
        self.limits.__post_init__()
        if type(self.source_image_limits) is not SourceImageLimits:
            raise AgentError("MISSING_SOURCE_LIMITS")
        self.source_image_limits.__post_init__()
        ceiling = PilotLimits()
        comparisons = (
            (self.limits.max_tool_calls, 8),
            (self.limits.max_model_calls, 8),
            (self.limits.max_iterations, 8),
            (self.limits.max_batch_images, 1),
            (self.limits.max_input_bytes, ceiling.max_bytes),
            (self.limits.max_pixels, ceiling.max_pixels),
            (self.limits.max_image_edge_px, ceiling.max_edge),
            (self.limits.max_input_tokens, 1024),
            (self.limits.max_output_tokens, 128),
            (self.limits.max_total_output_tokens, 1024),
            (self.limits.max_memory_entries, 8),
            (self.limits.max_response_chars, 8192),
            (self.limits.per_call_timeout_s, 60),
            (self.limits.per_image_timeout_s, 300),
            (self.limits.cleanup_timeout_s, 10),
            (self.load_timeout_s, 180),
            (self.session_timeout_s, 1800),
        )
        if any(type(v) not in (float, int) or not 0 < v <= maximum for v, maximum in comparisons):
            raise AgentError("RUNTIME_EXCEEDS_APPROVED_LIMITS")


def load_runtime_config(path: Path) -> RuntimeConfig:
    try:
        with path.open("rb") as stream:
            data = tomllib.load(stream)
        if (
            set(data) != {"schema", "adapter", "runtime", "limits", "source_image_limits"}
            or data["schema"] != "internvl-development-v2"
            or data["adapter"] != "internvl3-pinned"
        ):
            raise ValueError("schema")
        return RuntimeConfig(
            Limits(**data["limits"]),
            SourceImageLimits.from_dict(data["source_image_limits"]),
            **data["runtime"],
        )
    except (OSError, TypeError, ValueError) as exc:
        raise AgentError("INVALID_RUNTIME_CONFIG") from exc


def validate_request(request: Request, limits: Limits) -> None:
    allowed = {
        "caption": "caption",
        "scene": "query",
        "object": "query",
        "detail": "query",
        "verify": "query",
    }
    if (
        not isinstance(request, Request)
        or allowed.get(request.prompt_id) != request.tool
        or not isinstance(request.prompt, str)
        or not request.prompt.strip()
        or len(request.prompt) > limits.max_response_chars
        or type(request.max_output_tokens) is not int
        or not 1 <= request.max_output_tokens <= limits.max_output_tokens
    ):
        raise AgentError("INVALID_TOOL_REQUEST")
    if any(
        marker in request.prompt
        for marker in ("<image>", "<IMG_CONTEXT>", "<|im_start|>", "<|im_end|>", "<img>", "</img>")
    ):
        raise AgentError("RESERVED_TEMPLATE_TOKEN_IN_REQUEST")


def normalize_answer(raw: str, tokens: int, request: Request) -> Answer:
    """Literal clauses are candidate claims, never independent truth or calibrated confidence.

    These development heuristics only guide bounded Agent investigation. They do not
    reject execution, judge capability/adoption, translate, or repair model text.
    """
    if not isinstance(raw, str) or not raw.strip() or "\ufffd" in raw or tokens <= 0:
        raise AgentError("INVALID_TOOL_RESULT")
    uncertain = any(
        x in raw.lower()
        for x in (
            "不確定",
            "無法",
            "可能",
            "不明",
            "看不清",
            "矛盾",
            "不一致",
            "uncertain",
            "cannot",
            "maybe",
        )
    )
    verdict = "unresolved"
    if request.prompt_id == "verify":
        labels = set(re.findall(r"\b(supported|contradicted|unresolved)\b", raw.lower()))
        match = re.match(r"^\s*(supported|contradicted|unresolved)(?=\s|[.:：。]|$)", raw.lower())
        if match and labels == {match[1]}:
            verdict = match[1]
        return Answer(
            raw,
            uncertain=uncertain or verdict == "unresolved",
            verdict=verdict,
            output_tokens=tokens,
        )
    clauses = tuple(dict.fromkeys(x.strip() for x in re.split(r"[。！？\n]+", raw) if x.strip()))[
        :4
    ]
    missing: list[str] = []
    if uncertain:
        missing.append("detail" if request.prompt_id == "object" else "object")
    if any(x in raw for x in ("細節不明", "背景不明", "缺少細節", "矛盾", "不一致")):
        missing.append("detail")
    return Answer(raw, clauses, uncertain, tuple(dict.fromkeys(missing)), output_tokens=tokens)


def preprocess_array(path: Path, expected_hash: str, max_bytes: int) -> Any:
    """CPU preprocessing only, equivalent fixed tile policy used by both pilots.

    Caller must validate image bytes/hash/resolution first. Aspect ratio is warped;
    final preprocessing/tiling must be frozen for all A–D before formal evaluation.
    """
    import numpy as np
    from PIL import Image, ImageOps

    with path.open("rb") as handle:
        data = handle.read(max_bytes + 1)
    if len(data) > max_bytes or hashlib.sha256(data).hexdigest() != expected_hash:
        raise AgentError("IMAGE_CHANGED_OR_OVERSIZED")
    with Image.open(BytesIO(data)) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        resized = image.resize((448, 448), Image.Resampling.BICUBIC)
        array: Any = np.asarray(resized, dtype=np.float32) / 255.0
        array = (array - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array(
            [0.229, 0.224, 0.225], dtype=np.float32
        )
        image.close()
        resized.close()
    return array.transpose(2, 0, 1).copy()
