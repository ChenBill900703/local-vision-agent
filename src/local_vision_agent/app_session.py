"""Explicit application lifecycle; shares the legacy adapter and bounded Agent."""

import time
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from .agent import Agent
from .app_receipts import read_frame_receipts
from .contracts import ImageInput, Method, Report
from .internvl_adapter import InternVLAdapter
from .internvl_contract import RuntimeConfig
from .source_input import prepare_source


class AnalysisSession(Protocol):
    def analyze(self, item: ImageInput, input_directory: Path) -> Report: ...
    def close(self) -> dict[str, Any]: ...


class PersistentAnalysisSession:
    """One supervised model load, explicit image boundaries, no automatic retry."""

    def __init__(self, assets: Path, directory: Path, config: RuntimeConfig) -> None:
        self.config = config
        self.adapter = InternVLAdapter(assets, directory, config, persistent_images=True)
        self.closed = False
        self.busy = False
        self.used_ids: set[str] = set()
        self.cleanup_result: dict[str, Any] | None = None
        self.last_attempt: dict[str, Any] = {}

    def analyze(self, item: ImageInput, input_directory: Path) -> Report:
        if self.closed or self.busy or item.input_id in self.used_ids:
            raise RuntimeError("SESSION_CLOSED_BUSY_OR_DUPLICATE_INPUT")
        self.busy = True
        self.last_attempt = {"calls_complete": True, "frame_trace": []}
        report: Report | None = None
        started = time.monotonic()
        entered_runtime = False
        try:
            bounded, source = prepare_source(
                item, self.config.source_image_limits, self.config.limits, input_directory
            )
            self.last_attempt["source_input"] = source
            self.used_ids.add(item.input_id)
            entered_runtime = True
            if not self.adapter.loaded:
                self.adapter.load()
            self.adapter.begin_image(bounded)
            # Agent.run creates all observations/claims/counters afresh; no chat memory.
            report = Agent(self.config.limits, self.adapter, executor=self.adapter).run(
                bounded, Method.D
            )
            trace = list(self.adapter.trace)
            receipts, receipt_error = read_frame_receipts(self.adapter.directory, item.input_id)
            if receipts:
                trace = receipts
            boundary = self.adapter.end_image()
            measurements = [x.get("measurement", {}) for x in trace]
            allocated = [
                x["peak_allocated_bytes"] / 1048576
                for x in measurements
                if "peak_allocated_bytes" in x
            ]
            reserved = [
                x["peak_reserved_bytes"] / 1048576
                for x in measurements
                if "peak_reserved_bytes" in x
            ]
            return replace(
                report,
                model_latency_s=sum(x["latency_s"] for x in trace)
                if trace and all("latency_s" in x for x in trace)
                else None,
                peak_vram_mib=max(reserved) if reserved else None,
                runtime_metadata={
                    "source_input": source,
                    "image_end": boundary,
                    "model_runtime": self.adapter.metadata,
                    "frame_trace": trace,
                    "receipt_read_error": receipt_error,
                    "calls_complete": receipt_error is None,
                    "end_to_end_s": time.monotonic() - started,
                    "peak_allocated_mib": max(allocated) if allocated else None,
                    "observation_evidence": {
                        x["call_id"]: f"{self.adapter.directory}/events.jsonl"
                        f"#input={item.input_id}&call={x['call_id']}"
                        for x in trace
                    },
                    "same_model_verification_is_ground_truth": False,
                    "session_cleanup": "PENDING_SESSION_CLOSE",
                },
            )
        except Exception:
            receipts, receipt_error = read_frame_receipts(self.adapter.directory, item.input_id)
            self.last_attempt.update(
                frame_trace=receipts or list(self.adapter.trace),
                calls_complete=not entered_runtime or receipt_error is None,
                receipt_read_error=receipt_error,
            )
            if report is not None:
                self.last_attempt["report"] = asdict(report)
            # Invalid source before load is recoverable. A failed active runtime is not.
            if entered_runtime and (self.adapter.loaded or self.adapter.failed):
                self.close()
            raise
        finally:
            self.busy = False

    def close(self) -> dict[str, Any]:
        if self.closed:
            return dict(self.cleanup_result or {"already_closed": True})
        self.closed = True
        try:
            if self.adapter.loaded:
                self.cleanup_result = self.adapter.unload()
            else:
                self.adapter.transport.abort()
                self.cleanup_result = {"model_was_not_loaded": True}
            return dict(self.cleanup_result)
        except Exception as exc:
            self.cleanup_result = {"cleanup_error": str(exc)}
            raise


def session_identity() -> str:
    return "session-" + uuid4().hex
