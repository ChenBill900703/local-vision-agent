"""Qt worker ownership and explicit CPU demo, with shared report/history persistence."""

import json
import time
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage

from .agent import Agent
from .app_session import AnalysisSession
from .app_storage import AppStorage
from .contracts import Answer, ImageInfo, ImageInput, Method, Report, Request
from .internvl_contract import RuntimeConfig
from .mock_adapter import MockAdapter
from .reporting import to_json, to_markdown
from .source_input import prepare_source


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class AppRequest:
    identifier: str
    source: str
    path: Path
    directory: Path
    captured_at: str
    session_id: str
    save_frame: bool = False
    frame: QImage | None = None


class FakeAnalysisSession:
    """Explicit CPU demo only; no runtime fallback or image recognition."""

    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config
        self.closed = False

    def analyze(self, item: ImageInput, input_directory: Path) -> Report:
        if self.closed:
            raise RuntimeError("SESSION_CLOSED")
        bounded, provenance = prepare_source(
            item, self.config.source_image_limits, self.config.limits, input_directory
        )
        adapter = MockAdapter(
            answers={
                "caption": Answer("CPU模擬：" + item.input_id, (item.input_id,), output_tokens=20),
                "scene": Answer("CPU模擬場景。", output_tokens=8),
                "verify": Answer("unresolved", verdict="unresolved", output_tokens=2),
            }
        )

        class InlineFixture:
            def invoke(self, request: Request, image: ImageInfo, timeout_s: float) -> Answer:
                return adapter.invoke(request, image)

        report = Agent(self.config.limits, adapter, executor=InlineFixture()).run(bounded, Method.D)
        return replace(
            report,
            runtime_metadata={
                "source_input": provenance,
                "session_cleanup": "MOCK_NOT_PHYSICAL_EVIDENCE",
            },
        )

    def close(self) -> dict[str, Any]:
        self.closed = True
        return {"mock_cleanup": True, "gpu_measured": False}


class AnalysisWorker(QObject):
    result = Signal(str, object)
    preview = Signal(str, object)
    error = Signal(str, str)
    closed = Signal(object)

    def __init__(
        self, session: AnalysisSession, storage: AppStorage, config: RuntimeConfig
    ) -> None:
        super().__init__()
        self.session, self.storage, self.config = session, storage, config
        self.stopped = False
        self.completed_directories: list[Path] = []

    @Slot(str, str)
    def prepare_preview(self, identifier: str, path: str) -> None:
        try:
            directory = self.storage.allocate(identifier)
            bounded, _ = prepare_source(
                ImageInput(identifier, Path(path)),
                self.config.source_image_limits,
                self.config.limits,
                directory / "input",
            )
            # Return bounded bytes, never Qt widgets/pixmaps from this worker thread.
            self.preview.emit(identifier, bounded.path.read_bytes())
        except Exception as exc:  # noqa: BLE001 -- GUI receives explicit errors
            self.error.emit(identifier, str(exc))

    @Slot(object)
    def analyze(self, request: AppRequest) -> None:
        if self.stopped:
            self.error.emit(request.identifier, "SESSION_CLOSED")
            return
        started = time.monotonic()
        data: dict[str, Any] = {}
        try:
            if request.frame is not None:
                frame = request.frame
                if (
                    frame.isNull()
                    or max(frame.width(), frame.height())
                    > self.config.source_image_limits.max_source_edge_px
                    or frame.width() * frame.height()
                    > self.config.source_image_limits.max_decoded_pixels
                ):
                    raise ValueError("INVALID_CAMERA_FRAME")
                if not frame.save(str(request.path)):
                    raise OSError("CAMERA_FRAME_WRITE_FAILED")
                self.storage.save(
                    request.directory,
                    {
                        **inspect_capture(request.path),
                        "captured_at": request.captured_at,
                        "session_id": request.session_id,
                        "frame_id": request.identifier,
                    },
                    "capture.json",
                )
            analysis_started = time.monotonic()
            report = self.session.analyze(
                ImageInput(request.identifier, request.path), request.directory / "input"
            )
            analysis_elapsed = time.monotonic() - analysis_started
            data = {
                "schema": "windows-app-result-v1",
                "report_text": to_markdown(report),
                "report": json.loads(to_json(report)),
                "metadata": {
                    "status": report.status,
                    "analysis_latency_s": analysis_elapsed,
                    "error_type": report.stop_reason if report.status != "complete" else None,
                    "error_message": report.stop_reason if report.status != "complete" else None,
                    "calls": len(report.observations),
                    "tokens": sum(o.answer.output_tokens for o in report.observations if o.answer),
                    "truncated": any(o.answer.truncated for o in report.observations if o.answer),
                    "coverage": report.verification_coverage_ratio,
                    "stop_reason": report.stop_reason,
                    "allocated_mib": (report.runtime_metadata or {}).get("peak_allocated_mib"),
                    "reserved_mib": report.peak_vram_mib,
                    "evidence_kind": report.evidence_kind,
                },
            }
        except Exception as exc:  # noqa: BLE001 -- failed analyses are history too
            data = {
                "schema": "windows-app-result-v1",
                "report_text": "分析失敗：" + str(exc),
                "metadata": {
                    "status": "failed",
                    "stop_reason": str(exc),
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "evidence_kind": "MOCK_NOT_RESEARCH_EVIDENCE"
                    if isinstance(self.session, FakeAnalysisSession)
                    else "REAL_LOCAL_DEVELOPMENT_NOT_FORMAL_THESIS_RESULT",
                },
                "attempt_runtime": dict(getattr(self.session, "last_attempt", {})),
            }
        finally:
            if request.source == "WEBCAM" and not request.save_frame:
                try:
                    self.storage.remove_frame(request.directory)
                except OSError as exc:
                    data.setdefault("metadata", {}).update(status="failed", privacy_error=str(exc))
                    data["report_text"] = data.get("report_text", "") + "\n暫存影像清理失敗。"
        if data.get("attempt_runtime", {}).get("report"):
            data["report"] = data["attempt_runtime"]["report"]
        report_runtime = (data.get("report") or {}).get("runtime_metadata") or data.get(
            "attempt_runtime", {}
        )
        traces = report_runtime.get("frame_trace", [])
        device_values = [x.get("measurement", {}).get("nvidia", {}).get("used_mib") for x in traces]
        available = [x for x in device_values if type(x) in (int, float)]
        data["metadata"]["device_used_mib"] = max(available) if available else None
        data["metadata"].update(
            input_id=request.identifier,
            source=request.source,
            timestamp=timestamp(),
            captured_at=request.captured_at,
            session_id=request.session_id,
            latency_s=time.monotonic() - started,
            latency_scope="worker ingress through analysis/reset/ephemeral cleanup; excludes JSON flush, UI and wait",
        )
        try:
            capture = request.directory / "capture.json"
            if capture.exists():
                data["metadata"]["capture"] = json.loads(capture.read_text(encoding="utf-8"))
            target = self.storage.save(request.directory, data)
            self.completed_directories.append(request.directory)
            data["history_reference"] = str(target.relative_to(self.storage.root))
            self.result.emit(request.identifier, data)
        except Exception as exc:  # noqa: BLE001 -- never pretend persistence succeeded
            self.error.emit(request.identifier, "HISTORY_WRITE_FAILED:" + str(exc))

    @Slot()
    def close(self) -> None:
        if self.stopped:
            return
        self.stopped = True
        try:
            cleanup = self.session.close()
        except Exception as exc:  # noqa: BLE001 -- retain unverified cleanup
            cleanup = {"cleanup_error": str(exc)}
        try:
            for completed in self.completed_directories:
                self.storage.save(completed, cleanup, "session_cleanup.json")
            directory = self.storage.allocate("cleanup-" + str(time.time_ns()))
            self.storage.save(directory, cleanup, "cleanup.json")
        except OSError as exc:
            cleanup["persistence_error"] = str(exc)
        self.closed.emit(cleanup)


def inspect_capture(path: Path) -> dict[str, Any]:
    import hashlib

    with Image.open(path) as image:
        width, height = image.size
    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "width": width,
        "height": height,
    }
