"""Engineering-only capability scheduling. No semantic/language scoring or model imports."""

import math
from dataclasses import dataclass, fields
from typing import Any

from .internvl_policy import CORE, PROBES
from .pilot_policy import PilotLimits, PilotRefusal

RUN_ID = "INTERNVL3_AGENT_CAPABILITY_PILOT_20260928"
OPERATIONS = (("control", CORE[0][1]), *PROBES)


@dataclass(frozen=True)
class ExecutionReceipt:
    response: str
    decoded: bool
    worker_healthy: bool
    transport: str
    error: str | None
    input_tokens: int
    output_tokens: int
    image_output_tokens: int
    calls: int
    image_calls: int
    images: int
    elapsed_s: float
    image_elapsed_s: float
    session_elapsed_s: float
    reserved_mib: float
    free_mib: float

    def validate(self, limits: PilotLimits) -> None:
        if not isinstance(limits, PilotLimits):
            raise PilotRefusal("MISSING_SAFETY_LIMITS")
        if type(self.response) is not str or not self.response.strip() or "\ufffd" in self.response:
            raise PilotRefusal("EMPTY_OR_MALFORMED_OUTPUT")
        try:
            self.response.encode("utf8", errors="strict")
        except UnicodeError as exc:
            raise PilotRefusal("OUTPUT_DECODE_ERROR") from exc
        if (
            self.decoded is not True
            or self.worker_healthy is not True
            or self.transport != "completed"
            or self.error is not None
        ):
            raise PilotRefusal("UNHEALTHY_EXECUTION_OR_TRANSPORT")
        bounds = (
            (self.input_tokens, limits.max_input_tokens),
            (self.output_tokens, limits.max_output_tokens),
            (self.image_output_tokens, limits.max_output_per_image),
            (self.calls, limits.max_calls),
            (self.image_calls, limits.max_calls_per_image),
            (self.images, limits.max_images),
        )
        if any(type(value) is not int or not 1 <= value <= bound for value, bound in bounds):
            raise PilotRefusal("EXECUTION_TOKEN_CALL_IMAGE_BUDGET")
        if self.image_calls > self.calls or self.output_tokens > self.image_output_tokens:
            raise PilotRefusal("INCONSISTENT_BUDGET_RECEIPT")
        timed = (
            (self.elapsed_s, limits.call_s),
            (self.image_elapsed_s, limits.image_s),
            (self.session_elapsed_s, limits.session_s),
        )
        for value, bound in timed:
            if (
                type(value) not in (int, float)
                or not math.isfinite(value)
                or not 0 <= value <= bound
            ):
                raise PilotRefusal("EXECUTION_TIMEOUT")
        for value in (self.reserved_mib, self.free_mib):
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise PilotRefusal("INVALID_MEMORY_TELEMETRY")
        if self.reserved_mib > limits.allocator_cap_mib or self.free_mib < limits.reserve_mib:
            raise PilotRefusal("EXECUTION_MEMORY_BUDGET")


def validate_receipt(value: Any, limits: PilotLimits) -> ExecutionReceipt:
    if not isinstance(value, dict) or set(value) != {
        field.name for field in fields(ExecutionReceipt)
    }:
        raise PilotRefusal("MALFORMED_RECEIPT_SCHEMA")
    receipt = ExecutionReceipt(**value)
    receipt.validate(limits)
    return receipt


class CapabilityTransport:
    """Parent-side sequence checks, independent of worker self-reported health."""

    def __init__(self, limits: PilotLimits) -> None:
        self.limits = limits
        self.loaded = False
        self.image = False
        self.active: str | None = None
        self.completed = 0
        self.failed = False
        self.cleaning = False
        self.cleaned = False
        self.complete = False

    def observe(self, event: dict[str, Any]) -> None:
        phase = event.get("phase")
        if phase in {"failure", "network_violation", "cleanup_failure"}:
            self.failed = True
            self.active = None
            return
        if phase == "cleanup_start":
            self.cleaning = True
            self.active = None
            return
        if self.cleaning:
            if phase in {"before_cleanup", "workspace_cleanup"}:
                return
            if phase == "cleanup_done":
                m = event.get("measurement", {})
                if (
                    event.get("allocator_empty") is not True
                    or m.get("allocated_bytes") != 0
                    or m.get("reserved_bytes") != 0
                ):
                    raise PilotRefusal("CLEANUP_NOT_EMPTY")
                self.cleaned = True
                return
            if phase == "worker_done":
                if event.get("exit_code") == 0 and (
                    self.failed or not self.cleaned or not self.complete
                ):
                    raise PilotRefusal("FALSE_SUCCESS")
                return
            raise PilotRefusal("UNEXPECTED_CLEANUP_TRANSPORT")
        if self.failed:
            raise PilotRefusal("CONTINUED_AFTER_FAILURE")
        if phase in {"load_start", "preflight_pass", "cuda_baseline"} and not self.loaded:
            return
        if phase == "model_loaded" and not self.loaded:
            self.loaded = True
            return
        if phase == "image_start" and self.loaded and not self.image:
            self.image = True
            return
        if phase == "image_ready" and self.image and self.completed == 0:
            return
        if (
            phase == "call_start"
            and self.image
            and self.active is None
            and self.completed < len(OPERATIONS)
        ):
            name, prompt = OPERATIONS[self.completed]
            if event.get("operation") != name or event.get("prompt") != prompt:
                raise PilotRefusal("UNEXPECTED_PROBE_OR_PROMPT")
            self.active = name
            return
        if phase == "visual_done" and self.active and event.get("operation") == self.active:
            return
        if phase == "call_done" and self.active and event.get("operation") == self.active:
            receipt = validate_receipt(event.get("execution_receipt"), self.limits)
            if receipt.response != event.get("raw_response") or receipt.calls != self.completed + 1:
                raise PilotRefusal("TRANSPORT_RECEIPT_MISMATCH")
            self.completed += 1
            self.active = None
            return
        if phase == "pilot_complete" and self.completed == len(OPERATIONS) and self.active is None:
            self.complete = True
            return
        raise PilotRefusal("UNEXPECTED_TRANSPORT_STATE:" + str(phase))
