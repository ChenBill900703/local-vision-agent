"""Canonical Webcam lifecycle metadata. Physical success requires actual evidence."""

from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .app_controller import SessionLimits
from .app_storage import AppStorage


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class WebcamRecord:
    def __init__(
        self, storage: AppStorage, identifier: str, camera: dict[str, Any], limits: SessionLimits
    ) -> None:
        self.storage = storage
        self.directory: Path = storage.allocate(identifier)
        self.data: dict[str, Any] = {
            "schema": "webcam-session-v1",
            "session_id": identifier,
            **camera,
            "session_start_timestamp": utc_now(),
            "session_end_timestamp": None,
            "configured_post_analysis_interval_sec": limits.interval_s,
            "max_analysed_frames": limits.max_frames,
            "max_session_duration_sec": limits.max_duration_s,
            "limits": asdict(limits),
            "captured_frames": 0,
            "analysis_attempts": 0,
            "session_stop_reason": None,
            "camera_release_success": None,
            "worker_cleanup_success": None,
            "model_cleanup_success": None,
            "captured_frame_ids": [],
            "analysed_frame_ids": [],
        }
        self.save()

    def save(self) -> None:
        self.storage.save(self.directory, self.data, "session.json")

    def captured(self, identifier: str) -> None:
        self.data["captured_frame_ids"].append(identifier)
        self.data["captured_frames"] += 1
        self.save()

    def submitted(self, identifier: str) -> None:
        self.data["analysed_frame_ids"].append(identifier)
        self.data["analysis_attempts"] += 1
        self.save()

    def end(self, reason: str) -> None:
        if self.data["session_end_timestamp"] is None:
            self.data.update(
                session_end_timestamp=utc_now(),
                session_stop_reason=reason,
                camera_close_requested=True,
            )
            # Qt stop()/detach is a request, not physical release verification.
            self.save()

    def cleanup(self, value: dict[str, Any]) -> None:
        self.data["cleanup_evidence"] = value
        if self.data["camera_backend_type"] != "FAKE" and value.get("gpu_measured") is not False:
            measurement = value.get("measurement", {})
            self.data["worker_cleanup_success"] = (
                value.get("worker_exited") is True and value.get("job_empty") is True
                if "worker_exited" in value
                else None
            )
            self.data["model_cleanup_success"] = (
                measurement.get("allocated_bytes") == 0 and measurement.get("reserved_bytes") == 0
                if "allocated_bytes" in measurement
                else None
            )
            if value.get("cleanup_error"):
                self.data["worker_cleanup_success"] = self.data["model_cleanup_success"] = False
        self.save()
