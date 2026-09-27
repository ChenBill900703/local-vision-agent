"""Frozen first-pilot limits and fail-closed CPU validation; no torch import."""

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LABEL = "PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT"
MODEL_REVISION = "9a7d4024050840e001defacec2b00727e89149e6"
TOKENIZER_REVISION = "35192e10a54e36eabe0a7cc57a2c1aab371cafc5"
WEIGHT_HASH = "70a7d94c0c8349eb58ed2d9e636ef2d0916960f321ecabeac6354b8ba3d7403f"


@dataclass(frozen=True)
class PilotLimits:
    """Version 1, user-approved provisional safety limits, not thesis parameters."""

    estimated_peak_mib: int = 6000
    ceiling_mib: int = 6400
    reserve_mib: int = 1536
    allocator_cap_mib: int = 5400
    max_edge: int = 512
    max_pixels: int = 262144
    max_bytes: int = 10 * 1024 * 1024
    max_input_tokens: int = 1024
    max_output_tokens: int = 128
    max_calls_per_image: int = 8
    max_output_per_image: int = 1024
    max_images: int = 3
    max_calls: int = 24
    load_s: float = 180.0
    call_s: float = 60.0
    image_s: float = 300.0
    cleanup_s: float = 10.0
    session_s: float = 1800.0


class PilotRefusal(RuntimeError):
    pass


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def validate_assets(root: Path, *, repair: bool = False) -> dict[str, Any]:
    prefix = "controlled-repair1" if repair else "controlled"
    manifest_name = "controlled_repair1_manifest.json" if repair else "controlled_manifest.json"
    manifest = json.loads((root / "evidence" / manifest_name).read_text())
    if manifest["upstream_revision"] != MODEL_REVISION:
        raise PilotRefusal("REVISION_MISMATCH")
    for name, expected in manifest["files"].items():
        if Path(name).name != name:
            raise PilotRefusal("ASSET_PATH")
        if hash_file(root / prefix / "md2_fixed" / name) != expected:
            raise PilotRefusal("CONTROLLED_HASH_MISMATCH")
    if hash_file(root / "evidence" / f"{prefix}.patch") != manifest["patch_sha256"]:
        raise PilotRefusal("PATCH_HASH_MISMATCH")
    if hash_file(root / "upstream/model/model.safetensors") != WEIGHT_HASH:
        raise PilotRefusal("WEIGHT_HASH_MISMATCH")
    metadata = json.loads((root / "evidence/tokenizer_metadata.json").read_text())
    if metadata["sha"] != TOKENIZER_REVISION:
        raise PilotRefusal("TOKENIZER_REVISION_MISMATCH")
    return dict(manifest)


def validate_image(path: Path, expected_hash: str, limits: PilotLimits) -> None:
    if not path.is_file() or path.stat().st_size > limits.max_bytes:
        raise PilotRefusal("IMAGE_BYTES")
    if hash_file(path) != expected_hash:
        raise PilotRefusal("IMAGE_HASH")
    from PIL import Image

    with Image.open(path) as image:
        if image.format not in ("PNG", "JPEG") or getattr(image, "n_frames", 1) != 1:
            raise PilotRefusal("IMAGE_FORMAT")
        if max(image.size) > limits.max_edge or image.width * image.height > limits.max_pixels:
            raise PilotRefusal("IMAGE_RESOLUTION")
        image.verify()


class PilotBudget:
    def __init__(self, limits: PilotLimits, clock: Callable[[], float] = time.monotonic) -> None:
        self.limits = limits
        self.clock = clock
        self.started = clock()
        self.image_started = self.started
        self.calls = 0
        self.image_calls = 0
        self.output_tokens = 0
        self.images = 0

    def start_image(self) -> None:
        if self.images >= self.limits.max_images:
            raise PilotRefusal("IMAGE_COUNT")
        self.images += 1
        self.image_started = self.clock()
        self.image_calls = self.output_tokens = 0

    def before_call(self, input_tokens: int = 0, output_limit: int = 0) -> None:
        if self.clock() - self.started >= self.limits.session_s:
            raise PilotRefusal("SESSION_TIMEOUT")
        if self.clock() - self.image_started >= self.limits.image_s:
            raise PilotRefusal("IMAGE_TIMEOUT")
        if type(input_tokens) is not int or not 0 <= input_tokens <= self.limits.max_input_tokens:
            raise PilotRefusal("INPUT_TOKEN_LIMIT")
        if type(output_limit) is not int or not 0 <= output_limit <= self.limits.max_output_tokens:
            raise PilotRefusal("OUTPUT_TOKEN_LIMIT")
        if self.output_tokens + output_limit > self.limits.max_output_per_image:
            raise PilotRefusal("IMAGE_OUTPUT_LIMIT")
        if (
            self.calls >= self.limits.max_calls
            or self.image_calls >= self.limits.max_calls_per_image
        ):
            raise PilotRefusal("CALL_LIMIT")
        self.calls += 1
        self.image_calls += 1

    def after_call(self, output_tokens: int) -> None:
        if (
            type(output_tokens) is not int
            or not 0 <= output_tokens <= self.limits.max_output_tokens
        ):
            raise PilotRefusal("OUTPUT_TOKEN_LIMIT")
        self.output_tokens += output_tokens
        if self.output_tokens > self.limits.max_output_per_image:
            raise PilotRefusal("IMAGE_OUTPUT_LIMIT")
