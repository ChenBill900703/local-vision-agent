"""Parent-owned persistent JSON process with independent GPU/deadline watchdog."""

import hashlib
import json
import os
import queue
import subprocess
import sys
import threading
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .contracts import AgentError
from .gpu_guard import query_gpu_snapshot
from .internvl_contract import RuntimeConfig
from .pilot_ipc import EventReader
from .pilot_supervisor_repair import GpuSampler
from .windows_job import WindowsJob


class PersistentTransport:
    def __init__(self, root: Path, directory: Path, config: RuntimeConfig) -> None:
        self.root, self.directory, self.config = root, directory, config
        self.process: subprocess.Popen[str] | None = None
        self.job: WindowsJob | None = None
        self.reader: EventReader | None = None
        self.sampler: GpuSampler | None = None
        self.worker_pid: int | None = None
        self.failure: str | None = None
        self.started = self.deadline = self.image_deadline = 0.0
        self.phase = "load"
        self.last_sample = 0.0
        self.stop = threading.Event()
        self.lock = threading.RLock()
        self.watcher: threading.Thread | None = None
        self.next_id = 1
        self.closed = False
        self.owns_directory = False
        self.stderr: Any = None
        self.baseline: Any = None

    def _watch(self) -> None:
        assert self.sampler is not None
        while not self.stop.wait(0.02):
            try:
                now = time.monotonic()
                if now > self.deadline:
                    raise AgentError(self.phase.upper() + "_TIMEOUT")
                if self.image_deadline and now > self.image_deadline:
                    raise AgentError("IMAGE_TIMEOUT")
                if now - self.started > self.config.session_timeout_s:
                    raise AgentError("SESSION_TIMEOUT")
                while True:
                    try:
                        sample = self.sampler.samples.get_nowait()
                    except queue.Empty:
                        break
                    if isinstance(sample, Exception):
                        raise sample
                    self.last_sample, gpu = sample
                    with (self.directory / "device_samples.jsonl").open(
                        "a", encoding="utf8"
                    ) as handle:
                        handle.write(
                            json.dumps({"monotonic": self.last_sample, **asdict(gpu)}) + "\n"
                        )
                    if gpu.free_mib < 1536 or gpu.used_mib - self.baseline.used_mib > 6400:
                        raise AgentError("GPU_BUDGET")
                if now - self.last_sample > 2:
                    raise AgentError("GPU_TELEMETRY_STALE")
            except Exception as exc:  # noqa: BLE001 -- watchdog kills even between requests
                self.failure = str(exc)
                with self.lock:
                    if self.job is not None:
                        self.job.terminate(2)
                return

    def _receive(self, identifier: int, op: str, timeout: float) -> dict[str, Any]:
        assert self.reader is not None
        self.phase = op
        self.deadline = (
            min(time.monotonic() + timeout, self.started + self.config.load_timeout_s)
            if op == "load"
            else time.monotonic() + timeout
        )
        allowed = {
            "load_start",
            "preflight_pass",
            "cuda_baseline",
            "model_loaded",
            "image_start",
            "image_ready",
            "call_start",
            "visual_done",
            "call_done",
            "cleanup_start",
            "workspace_cleanup",
            "cleanup_done",
        }
        while True:
            if self.failure:
                raise AgentError(self.failure)
            if time.monotonic() > self.deadline:
                raise AgentError(op.upper() + "_TIMEOUT")
            try:
                event = self.reader.receive()
            except (EOFError, OSError, RuntimeError, ValueError) as exc:
                raise AgentError("WORKER_TRANSPORT_FAILURE") from exc
            if event is None:
                continue
            with (self.directory / "parent_trace.jsonl").open("a", encoding="utf8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
            if event.get("pid") != self.worker_pid:
                raise AgentError("WORKER_IDENTITY_MISMATCH")
            phase = event.get("phase")
            if phase in {"failure", "network_violation", "cleanup_failure"}:
                raise AgentError("WORKER_FAILURE:" + str(event.get("message", phase)))
            if phase == "response":
                if (
                    event.get("id") != identifier
                    or event.get("op") != op
                    or not isinstance(event.get("payload"), dict)
                ):
                    raise AgentError("RPC_RESPONSE_MISMATCH")
                if op != "unload":
                    self.deadline = self.started + self.config.session_timeout_s
                return dict(event["payload"])
            if phase not in allowed:
                raise AgentError("UNEXPECTED_WORKER_EVENT")

    def load(self) -> dict[str, Any]:
        if self.process is not None or self.closed:
            raise AgentError("MODEL_RELOAD_FORBIDDEN")
        self.directory.mkdir(parents=True, exist_ok=False)
        self.owns_directory = True
        configuration = self.directory / "runtime_config.json"
        configuration.write_text(json.dumps(asdict(self.config), indent=2), encoding="utf8")
        project = Path(__file__).resolve().parents[2]
        git = ["git", "-c", f"safe.directory={project.as_posix()}"]
        metadata = {
            "commit": subprocess.run(
                [*git, "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            ).stdout.strip(),
            "dirty_state": subprocess.run(
                [*git, "status", "--short"],
                capture_output=True,
                text=True,
                encoding="utf8",
                check=True,
            ).stdout,
            "source_hashes": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (project / "src/local_vision_agent").glob("*.py")
            },
            "label": "DEVELOPMENT ONLY / NOT FORMAL THESIS RESULT",
        }
        (self.directory / "provenance.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf8"
        )
        self.baseline = query_gpu_snapshot()
        (self.directory / "device_before.json").write_text(
            json.dumps(asdict(self.baseline)), encoding="utf8"
        )
        environment = dict(os.environ)
        environment.update(
            PYTHONPATH=str(project / "src"),
            PYTHONIOENCODING="utf-8",
            PYTHONDONTWRITEBYTECODE="1",
            HF_HUB_OFFLINE="1",
            TRANSFORMERS_OFFLINE="1",
            HF_HUB_DISABLE_TELEMETRY="1",
            HF_HOME=str(self.directory / "offline-cache"),
        )
        self.started = self.last_sample = time.monotonic()
        self.deadline = self.started + self.config.load_timeout_s
        try:
            self.job = WindowsJob()
            self.stderr = (self.directory / "stderr.txt").open("w", encoding="utf8")
            self.process = subprocess.Popen(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "local_vision_agent.internvl_rpc_worker",
                    "--root",
                    str(self.root),
                    "--run-dir",
                    str(self.directory),
                    "--configuration",
                    str(configuration),
                ],
                cwd=project,
                env=environment,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=self.stderr,
                text=True,
                encoding="utf8",
                bufsize=1,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            assert self.process.stdout is not None and self.process.stdin is not None
            self.reader = EventReader(self.process.stdout)
            ready = None
            while ready is None and time.monotonic() < self.deadline:
                ready = self.reader.receive()
            if ready is None or ready.get("phase") != "ready" or type(ready.get("pid")) is not int:
                raise AgentError("WORKER_HANDSHAKE")
            self.worker_pid = ready["pid"]
            self.job.assign(self.worker_pid)
            self.sampler = GpuSampler()
            self.watcher = threading.Thread(target=self._watch, daemon=True)
            self.watcher.start()
            self.process.stdin.write("GO\n")
            self.process.stdin.flush()
            return self._receive(0, "load", self.config.load_timeout_s)
        except Exception:
            self.abort()
            raise

    def request(self, op: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        if self.closed or self.process is None or self.process.poll() is not None or self.failure:
            raise AgentError("WORKER_NOT_HEALTHY")
        assert self.process.stdin is not None
        if op == "begin_image":
            self.image_deadline = time.monotonic() + self.config.limits.per_image_timeout_s
        if op == "unload":
            self.image_deadline = 0.0
        identifier = self.next_id
        self.next_id += 1
        try:
            line = json.dumps(
                {"id": identifier, "op": op, "payload": payload},
                ensure_ascii=False,
                allow_nan=False,
            )
            if len(line) > 65535:
                raise AgentError("RPC_REQUEST_TOO_LARGE")
            self.process.stdin.write(line + "\n")
            self.process.stdin.flush()
            return self._receive(identifier, op, timeout)
        except Exception:
            self.abort()
            raise

    def unload(self) -> dict[str, Any]:
        if self.closed:
            raise AgentError("WORKER_ALREADY_CLOSED")
        cleanup_started = time.monotonic()
        cleanup_deadline = cleanup_started + self.config.limits.cleanup_timeout_s
        result = self.request("unload", {}, self.config.limits.cleanup_timeout_s)
        m = result.get("measurement", {})
        if m.get("allocated_bytes") != 0 or m.get("reserved_bytes") != 0:
            self.abort()
            raise AgentError("CLEANUP_FAILED")
        assert self.process is not None and self.job is not None
        try:
            remaining = cleanup_deadline - time.monotonic()
            if remaining <= 0:
                raise AgentError("CLEANUP_TIMEOUT")
            self.process.wait(timeout=remaining)
            if self.process.returncode != 0 or self.job.active_count() != 0 or self.failure:
                raise AgentError("CLEANUP_FAILED")
        finally:
            self.abort()
        after = query_gpu_snapshot()
        result["device_after"] = asdict(after)
        result["job_empty"] = True
        result["worker_exited"] = True
        result["parent_cleanup_seconds"] = time.monotonic() - cleanup_started
        result["baseline_equivalent"] = (
            after.used_mib <= self.baseline.used_mib + 64
            and after.free_mib >= self.baseline.free_mib - 64
        )
        (self.directory / "cleanup_result.json").write_text(
            json.dumps(result, indent=2), encoding="utf8"
        )
        if not result["baseline_equivalent"]:
            raise AgentError("DEVICE_RECOVERY_FAILED")
        if time.monotonic() > cleanup_deadline:
            raise AgentError("CLEANUP_TIMEOUT")
        return result

    def abort(self) -> None:
        if self.closed:
            return
        self.stop.set()
        if self.watcher is not None:
            self.watcher.join(timeout=3)
        with self.lock:
            if self.job is not None:
                self.job.terminate(2)
                self.job.close()
                self.job = None
        if self.process is not None:
            if self.process.poll() is None:
                self.process.kill()
                self.process.wait(timeout=5)
            if self.process.stdin is not None:
                try:
                    self.process.stdin.close()
                except OSError:
                    pass
            if self.process.stdout is not None:
                self.process.stdout.close()
        if self.sampler is not None:
            self.sampler.stop.set()
            self.sampler.thread.join(timeout=0.1)
        if self.stderr is not None:
            self.stderr.close()
        self.closed = True
        if self.owns_directory:
            recovery: dict[str, Any] = {
                "worker_pid": self.worker_pid,
                "exit_code": self.process.returncode if self.process else None,
                "watchdog_failure": self.failure,
                "worker_exited": self.process is None or self.process.poll() is not None,
                "note": "Process exit is not proof of allocator-zero cleanup; see cleanup_result separately.",
            }
            try:
                recovery["device_after_exit"] = asdict(query_gpu_snapshot())
            except Exception as exc:  # noqa: BLE001 -- failed telemetry must remain visible
                recovery["recovery_query_error"] = str(exc)
            (self.directory / "termination_result.json").write_text(
                json.dumps(recovery, indent=2), encoding="utf8"
            )
