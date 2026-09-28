"""Typed real VLM boundary. Explicit load/unload; never silently substitutes a mock."""

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .contracts import AgentError, Answer, ImageInfo, ImageInput, Request
from .image_input import inspect_image
from .internvl_contract import RuntimeConfig, normalize_answer, validate_request
from .internvl_policy import REVISION
from .internvl_transport import PersistentTransport


class InternVLAdapter:
    model_id = "OpenGVLab/InternVL3-2B-Instruct"
    revision = REVISION
    is_mock = False
    capabilities: tuple[str, ...] = ("caption", "query")

    def __init__(self, asset_root: Path, evidence_directory: Path, config: RuntimeConfig) -> None:
        if type(config) is not RuntimeConfig:
            raise AgentError("MISSING_RUNTIME_CONFIG")
        config.__post_init__()
        self.config = config
        self.directory = evidence_directory.resolve()
        self.transport = PersistentTransport(asset_root.resolve(), self.directory, config)
        self.metadata: dict[str, Any] = {}
        self.trace: list[dict[str, Any]] = []
        self.image: ImageInfo | None = None
        self.loaded = False
        self.failed = False
        self.cleanup: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        if self.loaded or self.failed:
            raise AgentError("MODEL_RELOAD_FORBIDDEN")
        try:
            self.metadata = self.transport.load()
            if (
                self.metadata.get("model_id") != self.model_id
                or self.metadata.get("revision") != self.revision
                or self.metadata.get("device") != "cuda:0"
            ):
                raise AgentError("MODEL_METADATA_MISMATCH")
            self.loaded = True
            return dict(self.metadata)
        except Exception as exc:
            self.failed = True
            self.transport.abort()
            if isinstance(exc, AgentError):
                raise
            raise AgentError("WORKER_FAILURE") from exc

    def begin_image(self, item: ImageInput) -> ImageInfo:
        if not self.loaded or self.failed or self.image is not None:
            raise AgentError("ONE_IMAGE_PER_WORKER")
        image = inspect_image(item, self.config.limits)
        try:
            result = self.transport.request(
                "begin_image",
                {
                    "input_id": item.input_id,
                    "path": str(item.path.resolve()),
                    "sha256": image.sha256,
                },
                self.config.limits.per_call_timeout_s,
            )
            if (
                result.get("image") != asdict(image)
                or result.get("preprocessing") != self.config.preprocessing
                or result.get("tile_count") != 1
            ):
                raise AgentError("PREPROCESSING_METADATA_MISMATCH")
            self.image = image
            return image
        except Exception as exc:
            self.failed = True
            self.transport.abort()
            if isinstance(exc, AgentError):
                raise
            raise AgentError("WORKER_FAILURE") from exc

    def invoke(self, request: Request, image: ImageInfo, timeout_s: float | None = None) -> Answer:
        validate_request(request, self.config.limits)
        if not self.loaded or self.failed or self.image is None or image != self.image:
            raise AgentError("MODEL_OR_IMAGE_NOT_READY")
        if len(self.trace) >= min(
            self.config.limits.max_tool_calls, self.config.limits.max_model_calls
        ):
            raise AgentError("MODEL_CALL_LIMIT")
        timeout = self.config.limits.per_call_timeout_s if timeout_s is None else timeout_s
        if (
            type(timeout) not in (int, float)
            or not 0 < timeout <= self.config.limits.per_call_timeout_s
        ):
            raise AgentError("INVALID_CALL_TIMEOUT")
        try:
            result = self.transport.request("invoke", asdict(request), timeout)
            tokens = result.get("output_tokens")
            if type(tokens) is not int or not 0 < tokens <= request.max_output_tokens:
                raise AgentError("INVALID_TOKEN_RECEIPT")
            raw = result.get("raw_response")
            if not isinstance(raw, str):
                raise AgentError("INVALID_TOOL_RESULT")
            answer = normalize_answer(raw, tokens, request)
            if len(raw) + sum(map(len, answer.claims)) > self.config.limits.max_response_chars:
                raise AgentError("OUTPUT_LIMIT")
            self.trace.append({"request": asdict(request), **result})
            return answer
        except Exception as exc:
            self.failed = True
            self.transport.abort()
            if isinstance(exc, AgentError):
                raise
            raise AgentError("WORKER_FAILURE") from exc

    def caption(self) -> Answer:
        return self.query(
            "請使用繁體中文描述圖片可見的場景、物件與細節；不確定時明示。", prompt_id="caption"
        )

    def query(self, prompt: str, *, prompt_id: str = "scene") -> Answer:
        if self.image is None:
            raise AgentError("IMAGE_NOT_READY")
        return self.invoke(
            Request(
                "caption" if prompt_id == "caption" else "query",
                prompt_id,
                prompt,
                self.config.limits.max_output_tokens,
            ),
            self.image,
        )

    def health(self) -> dict[str, Any]:
        process = self.transport.process
        return {
            "loaded": self.loaded,
            "failed": self.failed,
            "worker_alive": process is not None and process.poll() is None,
            "watchdog_failure": self.transport.failure,
            "calls": len(self.trace),
        }

    def unload(self) -> dict[str, Any]:
        try:
            if self.failed:
                self.transport.abort()
                raise AgentError("CLEANUP_UNVERIFIED_AFTER_FAILURE")
            self.cleanup = self.transport.unload()
            return dict(self.cleanup)
        finally:
            self.loaded = False
            self.image = None
