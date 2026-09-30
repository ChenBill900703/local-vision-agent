"""Bounded CPU-only original ingress; model-facing limits stay independently fixed."""

import hashlib
import json
import warnings
from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageFile, ImageOps, UnidentifiedImageError

from .contracts import AgentError, ImageInput, Limits
from .image_input import inspect_image


@dataclass(frozen=True)
class SourceImageLimits:
    max_compressed_bytes: int
    max_decoded_pixels: int
    max_source_edge_px: int
    formats: tuple[str, ...]

    def __post_init__(self) -> None:
        for value, ceiling in (
            (self.max_compressed_bytes, 32 * 1024 * 1024),
            (self.max_decoded_pixels, 32_000_000),
            (self.max_source_edge_px, 10000),
        ):
            if type(value) is not int or not 0 < value <= ceiling:
                raise AgentError("INVALID_SOURCE_LIMITS")
        if self.formats != ("JPEG", "PNG"):
            raise AgentError("INVALID_SOURCE_FORMATS")

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "SourceImageLimits":
        data = dict(values)
        if not isinstance(data.get("formats"), list):
            raise AgentError("INVALID_SOURCE_FORMATS")
        data["formats"] = tuple(data["formats"])
        return cls(**data)


def prepare_source(
    item: ImageInput, source: SourceImageLimits, model_limits: Limits, directory: Path
) -> tuple[ImageInput, dict[str, Any]]:
    """Validate bytes before decode; persist only an automatically reduced large input.

    Directory must be private ignored run-input storage. Original is never written.
    This function does not import model frameworks or query GPU.
    """
    source.__post_init__()
    if not item.input_id.strip() or len(item.input_id) > 128:
        raise AgentError("INVALID_INPUT_ID")
    if ImageFile.LOAD_TRUNCATED_IMAGES:
        raise AgentError("UNSAFE_PILLOW_TRUNCATED_SETTING")
    try:
        with item.path.open("rb") as stream:
            data = stream.read(source.max_compressed_bytes + 1)
    except OSError as exc:
        raise AgentError("IMAGE_IO_ERROR") from exc
    if len(data) > source.max_compressed_bytes:
        raise AgentError("SOURCE_BYTES_LIMIT")
    sha = hashlib.sha256(data).hexdigest()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as opened:
                width, height = opened.size
                fmt = opened.format
                if fmt not in source.formats or getattr(opened, "n_frames", 1) != 1:
                    raise AgentError("UNSUPPORTED_IMAGE")
                if width * height > source.max_decoded_pixels:
                    raise AgentError("SOURCE_PIXELS_LIMIT")
                if max(width, height) > source.max_source_edge_px:
                    raise AgentError("SOURCE_EDGE_LIMIT")
                opened.verify()
            with Image.open(BytesIO(data)) as opened:
                opened.load()
                oriented = ImageOps.exif_transpose(opened)
                try:
                    rgb = oriented.convert("RGB")
                finally:
                    oriented.close()
                try:
                    metadata: dict[str, Any] = {
                        "policy": "smartphone-source-v1",
                        "source_path": str(item.path.resolve()),
                        "source_sha256": sha,
                        "source_bytes": len(data),
                        "source_width": width,
                        "source_height": height,
                        "source_format": fmt,
                        "oriented_width": rgb.width,
                        "oriented_height": rgb.height,
                        "source_image_limits": asdict(source),
                    }
                    small = (
                        max(width, height) <= model_limits.max_image_edge_px
                        and width * height <= model_limits.max_pixels
                        and len(data) <= model_limits.max_input_bytes
                    )
                    if small:
                        info = inspect_image(item, model_limits)
                        if info.sha256 != sha:
                            raise AgentError("SOURCE_CHANGED")
                        metadata.update(
                            normalized=False,
                            model_input_path=str(item.path.resolve()),
                            model_input=asdict(info),
                            conversion="identity: existing bounded image path",
                        )
                        return item, metadata
                    rgb.thumbnail(
                        (model_limits.max_image_edge_px, model_limits.max_image_edge_px),
                        Image.Resampling.LANCZOS,
                    )
                    clean = Image.frombytes("RGB", rgb.size, rgb.tobytes())
                    try:
                        encoded = BytesIO()
                        clean.save(encoded, format="PNG")
                        normalized = encoded.getvalue()
                    finally:
                        clean.close()
                    if (
                        len(normalized) > model_limits.max_input_bytes
                        or rgb.width * rgb.height > model_limits.max_pixels
                    ):
                        raise AgentError("NORMALIZED_IMAGE_LIMIT")
                    directory.mkdir(parents=True, exist_ok=False)
                    target = directory / "normalized.png"
                    target.write_bytes(normalized)
                    bounded = ImageInput(item.input_id, target)
                    info = inspect_image(bounded, model_limits)
                    metadata.update(
                        normalized=True,
                        model_input_path=str(target.resolve()),
                        model_input=asdict(info),
                        conversion="EXIF transpose/RGB/LANCZOS aspect-preserving <=512/metadata-free PNG",
                    )
                    (directory / "source_provenance.json").write_text(
                        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf8"
                    )
                    return bounded, metadata
                finally:
                    rgb.close()
    except (
        OSError,
        ValueError,
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise AgentError("INVALID_IMAGE") from exc
