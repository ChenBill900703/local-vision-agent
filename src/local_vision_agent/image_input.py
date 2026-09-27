"""Bounded CPU image validation. Images are never interpreted by the mock."""

import hashlib
import warnings
from io import BytesIO

from .contracts import AgentError, ImageInfo, ImageInput, Limits


def inspect_image(item: ImageInput, limits: Limits) -> ImageInfo:
    if not isinstance(item.input_id, str) or not item.input_id.strip() or len(item.input_id) > 128:
        raise AgentError("INVALID_INPUT_ID")
    try:
        with item.path.open("rb") as handle:
            data = handle.read(limits.max_input_bytes + 1)
        if len(data) > limits.max_input_bytes:
            raise AgentError("IMAGE_BYTES_LIMIT")
        from PIL import Image, ImageOps, UnidentifiedImageError
    except ImportError as exc:
        raise AgentError("MISSING_DEPENDENCY:Pillow") from exc
    except OSError as exc:
        raise AgentError("IMAGE_IO_ERROR") from exc
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as image:
                image_format = image.format
                if image_format not in ("PNG", "JPEG") or getattr(image, "n_frames", 1) != 1:
                    raise AgentError("UNSUPPORTED_IMAGE")
                if image.width * image.height > limits.max_pixels:
                    raise AgentError("IMAGE_PIXELS_LIMIT")
                if max(image.size) > limits.max_image_edge_px:
                    raise AgentError("IMAGE_EDGE_LIMIT")
                image.verify()
            with Image.open(BytesIO(data)) as image:
                # Force full decoding; EXIF orientation then RGB, no silent resizing.
                rgb = ImageOps.exif_transpose(image).convert("RGB")
                rgb.load()
                width, height = rgb.size
                rgb.close()
        return ImageInfo(hashlib.sha256(data).hexdigest(), width, height, image_format)
    except (
        OSError,
        ValueError,
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise AgentError("INVALID_IMAGE") from exc
