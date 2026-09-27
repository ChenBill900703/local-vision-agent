"""Pipe event transport and deadlines; no shared status file or GPU imports."""

import json
import queue
import threading
from dataclasses import dataclass
from typing import IO, Any

from .pilot_policy import PilotLimits, PilotRefusal


class EventReader:
    def __init__(self, stream: IO[str]) -> None:
        self.queue: queue.Queue[dict[str, Any] | Exception | None] = queue.Queue()
        self.thread = threading.Thread(target=self._read, args=(stream,), daemon=True)
        self.thread.start()

    def _read(self, stream: IO[str]) -> None:
        try:
            for line in stream:
                record = json.loads(line)
                if not isinstance(record, dict) or not isinstance(record.get("phase"), str):
                    raise PilotRefusal("INVALID_IPC_EVENT")
                self.queue.put(record)
        except Exception as exc:  # noqa: BLE001 -- propagate reader failures to supervisor
            self.queue.put(exc)
        finally:
            self.queue.put(None)

    def receive(self, timeout: float = 0.05) -> dict[str, Any] | None:
        try:
            value = self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
        if value is None:
            raise EOFError("WORKER_PIPE_CLOSED")
        if isinstance(value, Exception):
            raise PilotRefusal(f"IPC_ERROR:{value}") from value
        return value


@dataclass
class Deadlines:
    started: float
    limits: PilotLimits
    loaded: bool = False
    call_started: float | None = None
    image_started: float | None = None
    cleanup_started: float | None = None
    done: bool = False

    def observe(self, event: dict[str, Any]) -> None:
        phase, timestamp = event["phase"], float(event["monotonic"])
        if phase == "model_loaded":
            self.loaded = True
        elif phase == "image_start":
            self.image_started = timestamp
        elif phase == "call_start":
            self.call_started = timestamp
        elif phase == "call_done":
            if self.call_started is None or timestamp - self.call_started > self.limits.call_s:
                raise PilotRefusal("CALL_TIMEOUT_OR_MISSING_START")
            self.call_started = None
        elif phase in {"failure", "cleanup_start"}:
            if self.cleanup_started is None:
                self.cleanup_started = timestamp
            self.call_started = self.image_started = None
        elif phase == "worker_done":
            self.done = True

    def check(self, now: float) -> None:
        if now - self.started > self.limits.session_s:
            raise PilotRefusal("SESSION_TIMEOUT")
        if self.cleanup_started is not None:
            if now - self.cleanup_started > self.limits.cleanup_s:
                raise PilotRefusal("CLEANUP_TIMEOUT")
            return
        if not self.loaded and now - self.started > self.limits.load_s:
            raise PilotRefusal("LOAD_TIMEOUT")
        if self.call_started is not None and now - self.call_started > self.limits.call_s:
            raise PilotRefusal("CALL_TIMEOUT")
        if self.image_started is not None and now - self.image_started > self.limits.image_s:
            raise PilotRefusal("IMAGE_TIMEOUT")
