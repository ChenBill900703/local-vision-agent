"""Versioned CPU-only engineering contracts; no model framework imports."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, fields
from enum import StrEnum
from math import isfinite
from pathlib import Path
from typing import Protocol


class AgentError(RuntimeError):
    """Stable machine-readable failure code, suitable for partial reports."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class Method(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


@dataclass(frozen=True)
class Limits:
    max_tool_calls: int
    max_model_calls: int
    max_iterations: int
    per_call_timeout_s: float
    per_image_timeout_s: float
    cleanup_timeout_s: float
    max_input_bytes: int
    max_pixels: int
    max_image_edge_px: int
    max_input_tokens: int
    max_output_tokens: int
    max_total_output_tokens: int
    max_response_chars: int
    max_memory_entries: int
    max_batch_images: int

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name.endswith("_s"):
                valid = type(value) in (int, float) and isfinite(value) and value > 0
            else:
                valid = type(value) is int and value > 0
            if not valid:
                raise AgentError("INVALID_LIMIT:" + field.name)


def load_limits(path: Path) -> Limits:
    """No defaults; reject legacy configuration, typos and omitted limits."""
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        if set(data) != {"schema", "adapter", "limits"}:
            raise ValueError("unknown configuration")
        if data["schema"] != "agent-mock-v1" or data["adapter"] != "mock":
            raise ValueError("only explicit mock is implemented")
        return Limits(**data["limits"])
    except (OSError, ValueError, TypeError) as exc:
        raise AgentError("INVALID_CONFIG") from exc


@dataclass(frozen=True)
class ImageInput:
    input_id: str
    path: Path


@dataclass(frozen=True)
class ImageInfo:
    sha256: str
    width: int
    height: int
    format: str


@dataclass(frozen=True)
class Request:
    tool: str
    prompt_id: str
    prompt: str
    max_output_tokens: int
    claim: str | None = None


@dataclass(frozen=True)
class Answer:
    text: str
    claims: tuple[str, ...] = ()
    uncertain: bool = False
    missing: tuple[str, ...] = ()
    verdict: str = "unresolved"
    output_tokens: int = 0


class VisionAdapter(Protocol):
    """Future adapters must normalize bounded output; same instance identity for A-D.

    Call inside a controlled worker. No tool may execute instructions in model output.
    A real adapter needs separately approved loading/preflight and token accounting.
    """

    @property
    def model_id(self) -> str: ...

    @property
    def revision(self) -> str: ...

    @property
    def is_mock(self) -> bool: ...

    @property
    def capabilities(self) -> tuple[str, ...]: ...

    def invoke(self, request: Request, image: ImageInfo) -> Answer: ...


class Executor(Protocol):
    def invoke(self, request: Request, image: ImageInfo, timeout_s: float) -> Answer: ...


@dataclass(frozen=True)
class Observation:
    call_id: str
    state: str
    request: Request
    answer: Answer | None
    error: str | None


@dataclass(frozen=True)
class Claim:
    text: str
    observation_ids: tuple[str, ...]
    status: str = "model-proposed"
    verification_id: str | None = None


@dataclass(frozen=True)
class Report:
    run_id: str
    input_id: str
    method: Method
    status: str
    stop_reason: str
    investigation_stop: str
    image: ImageInfo | None
    observations: tuple[Observation, ...]
    claims: tuple[Claim, ...]
    states: tuple[str, ...]
    limits: Limits
    model_id: str = "mock-scripted"
    model_revision: str = "fixture-v1"
    evidence_kind: str = "MOCK_NOT_RESEARCH_EVIDENCE"
    schema_version: str = "agent-report-v1"
    policy_revision: str = "bounded-policy-v1"
    peak_vram_mib: float | None = None
    model_latency_s: float | None = None
    runtime_metadata: dict[str, object] | None = None
