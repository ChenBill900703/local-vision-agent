"""Clock-injected sequential scheduling. No Qt, hardware, queue, or model imports."""

import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from .app_session import session_identity


class AppState(StrEnum):
    IDLE = "IDLE"
    IMAGE_READY = "IMAGE_READY"
    MODEL_LOADING = "MODEL_LOADING"
    ANALYZING_IMAGE = "ANALYZING_IMAGE"
    WEBCAM_PREVIEW = "WEBCAM_PREVIEW"
    WEBCAM_AUTO_ANALYZING = "WEBCAM_AUTO_ANALYZING"
    STOPPING = "STOPPING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class SessionLimits:
    interval_s: int = 5
    max_frames: int = 20
    max_duration_s: int = 1800

    def __post_init__(self) -> None:
        for value, low, high in (
            (self.interval_s, 3, 30),
            (self.max_frames, 1, 20),
            (self.max_duration_s, 1, 1800),
        ):
            if type(value) is not int or not low <= value <= high:
                raise ValueError("INVALID_SESSION_LIMITS")


class AppController:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self.clock = clock
        self.state = AppState.IDLE
        self.busy = self.auto = self.stopping = self.closing = False
        self.session_id = session_identity()
        self.frame_count = 0
        self.deadline = self.next_due = 0.0
        self.pending: str | None = None
        self.limits = SessionLimits()

    def select_image(self) -> None:
        if self.busy or self.auto or self.closing:
            raise RuntimeError("BUSY")
        self.state = AppState.IMAGE_READY

    def start_auto(self, limits: SessionLimits) -> None:
        if self.busy or self.auto or self.closing:
            raise RuntimeError("BUSY")
        self.limits = limits
        self.session_id = session_identity()
        self.frame_count = 0
        self.deadline = self.clock() + limits.max_duration_s
        self.next_due = self.clock()
        self.auto, self.stopping = True, False
        self.state = AppState.WEBCAM_PREVIEW

    def request(self, source: str) -> str | None:
        if self.busy or self.stopping or self.closing:
            return None
        if source == "WEBCAM":
            if not self.auto:
                return None
            if self.clock() >= self.deadline or self.frame_count >= self.limits.max_frames:
                self.stop()
                return None
            if self.clock() < self.next_due:
                return None
            self.frame_count += 1
            identifier = f"{self.session_id}-frame-{self.frame_count:04d}"
        elif source == "IMAGE" and not self.auto and self.state == AppState.IMAGE_READY:
            identifier = "image-" + session_identity()
        else:
            return None
        self.busy = True
        self.pending = identifier
        self.state = (
            AppState.WEBCAM_AUTO_ANALYZING if source == "WEBCAM" else AppState.ANALYZING_IMAGE
        )
        return identifier

    def complete(self, identifier: str, success: bool) -> bool:
        if identifier != self.pending:
            return False
        self.pending = None
        self.busy = False
        if not success:
            self.auto = False
            self.state = AppState.ERROR
        elif self.stopping or self.closing:
            self.state = AppState.IDLE
        elif self.auto:
            self.next_due = self.clock() + self.limits.interval_s
            self.state = AppState.WEBCAM_PREVIEW
        else:
            self.state = AppState.IMAGE_READY
        return True

    def stop(self) -> None:
        self.auto = False
        self.stopping = True
        self.state = AppState.STOPPING if self.busy else AppState.IDLE

    def recover(self) -> None:
        if self.busy or self.closing:
            raise RuntimeError("BUSY")
        self.stopping = False
        self.state = AppState.IDLE

    def close(self) -> None:
        self.closing = True
        self.stop()
