"""Repair pilot: gated worker, pipe deadlines, Windows kernel process-tree ownership."""

import argparse
import hashlib
import json
import os
import queue
import subprocess
import sys
import threading
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .capability_gate import RUN_ID as CAPABILITY_RUN_ID
from .capability_gate import CapabilityTransport
from .gpu_guard import GpuSnapshot, query_gpu_snapshot
from .language_diagnostic import RUN_ID
from .pilot_ipc import Deadlines, EventReader
from .pilot_policy import LABEL, PilotLimits, PilotRefusal
from .pilot_supervisor import stop_process, windows_memory
from .windows_job import WindowsJob


class GpuSampler:
    """NVIDIA queries cannot block deadlines. Stale/error telemetry fails closed."""

    def __init__(self) -> None:
        self.samples: queue.Queue[tuple[float, GpuSnapshot] | Exception] = queue.Queue()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self) -> None:
        try:
            while not self.stop.is_set():
                self.samples.put((time.monotonic(), query_gpu_snapshot()))
                self.stop.wait(0.5)
        except Exception as exc:  # noqa: BLE001 -- propagate telemetry failure
            self.samples.put(exc)


def run(
    root: Path,
    authorized: bool,
    *,
    final_language: bool = False,
    internvl: bool = False,
    capability: bool = False,
) -> int:
    if not authorized:
        raise PilotRefusal("EXPLICIT_REPAIR1_AUTHORIZATION_REQUIRED")
    if capability:
        internvl = True
    if internvl and final_language:
        raise PilotRefusal("CONFLICTING_PILOT_MODES")
    limits = PilotLimits()
    run_id = (
        "INTERNVL3_INITIAL_GPU_PILOT"
        if internvl
        else (RUN_ID if final_language else "repair1-pilot")
    )
    if capability:
        run_id = CAPABILITY_RUN_ID
    run_dir = root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    project = Path(__file__).resolve().parents[2]

    def git_read(*args: str) -> str:
        return subprocess.run(
            ["git", "-c", f"safe.directory={project.as_posix()}", *args],
            cwd=project,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout.strip()

    metadata = {
        "label": LABEL,
        "amendment": run_id,
        "started": datetime.now().astimezone().isoformat(),
        "commit": git_read("rev-parse", "HEAD"),
        "dirty_state": git_read("status", "--porcelain"),
        "limits": asdict(limits),
        "source_hashes": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (project / "src/local_vision_agent").glob("*.py")
        },
    }
    (run_dir / "provenance.json").write_text(json.dumps(metadata, indent=2), encoding="utf8")
    (run_dir / "windows_before.json").write_text(json.dumps(windows_memory(), indent=2))
    before = query_gpu_snapshot()
    (run_dir / "device_before.json").write_text(json.dumps(asdict(before), indent=2))
    environment = dict(os.environ)
    environment.update(
        PYTHONPATH=str(project / "src"),
        PYTHONIOENCODING="utf-8",
        PYTHONDONTWRITEBYTECODE="1",
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
        HF_HOME=str(root / "runtime-cache"),
        HF_HUB_DISABLE_TELEMETRY="1",
    )
    started = time.monotonic()
    deadlines = Deadlines(started, limits)
    transport = CapabilityTransport(limits) if capability else None
    failure: str | None = None
    process = job = sampler = None
    worker_pid = worker_exit = None
    job_empty = False
    try:
        job = WindowsJob()
        with (run_dir / "stderr.txt").open("w", encoding="utf8") as stderr:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "local_vision_agent.internvl_worker"
                    if internvl
                    else "local_vision_agent.pilot_worker",
                    "--root",
                    str(root),
                    "--run-dir",
                    str(run_dir),
                    *(
                        ["--capability"]
                        if capability
                        else []
                        if internvl
                        else ["--final-language" if final_language else "--repair1"]
                    ),
                ],
                cwd=project,
                env=environment,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=stderr,
                text=True,
                encoding="utf8",
                bufsize=1,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            assert process.stdout is not None and process.stdin is not None
            reader = EventReader(process.stdout)
            sampler = GpuSampler()
            last_sample = started
            with (run_dir / "pipe_events.jsonl").open("w", encoding="utf8") as trace:
                while not deadlines.done:
                    deadlines.check(time.monotonic())
                    event = reader.receive()
                    if event is not None:
                        trace.write(json.dumps(event, ensure_ascii=False) + "\n")
                        trace.flush()
                        if event["phase"] == "ready":
                            if worker_pid is not None:
                                raise PilotRefusal("DUPLICATE_READY")
                            worker_pid = int(event["pid"])
                            job.assign(worker_pid)
                            process.stdin.write("GO\n")
                            process.stdin.flush()
                            process.stdin.close()
                        else:
                            if worker_pid is None or event["pid"] != worker_pid:
                                raise PilotRefusal("WORKER_IDENTITY_MISMATCH")
                            if transport is not None:
                                transport.observe(event)
                            deadlines.observe(event)
                            print(event["phase"], event.get("operation", ""), flush=True)
                            if event["phase"] == "worker_done":
                                worker_exit = int(event["exit_code"])
                    while not sampler.samples.empty():
                        item = sampler.samples.get_nowait()
                        if isinstance(item, Exception):
                            raise item
                        last_sample, sample = item
                        with (run_dir / "device_samples.jsonl").open("a") as handle:
                            handle.write(
                                json.dumps({"monotonic": last_sample, **asdict(sample)}) + "\n"
                            )
                        if sample.free_mib < limits.reserve_mib:
                            raise PilotRefusal("DEDICATED_FREE_RESERVE")
                        if sample.used_mib - before.used_mib > limits.ceiling_mib:
                            raise PilotRefusal("DEVICE_USAGE_CEILING")
                    if time.monotonic() - last_sample > 2:
                        raise PilotRefusal("GPU_TELEMETRY_STALE")
                process.wait(timeout=limits.cleanup_s)
                job_empty = job.active_count() == 0
                if not job_empty:
                    raise PilotRefusal("WORKER_DESCENDANTS_REMAIN")
    except Exception as exc:  # noqa: BLE001 -- all failures must terminate the complete job
        failure = f"SUPERVISOR_ERROR:{type(exc).__name__}:{exc}"
    finally:
        if sampler is not None:
            sampler.stop.set()
        try:
            if job is not None:
                job.terminate(limits.cleanup_s / 2)
                job_empty = job.active_count() == 0
        finally:
            if job is not None:
                job.close()
            if process is not None:
                stop_process(process, limits.cleanup_s / 2)
                if process.stdout is not None:
                    process.stdout.close()
        if sampler is not None:
            sampler.thread.join(timeout=0.1)
    after = query_gpu_snapshot()
    (run_dir / "windows_after.json").write_text(json.dumps(windows_memory(), indent=2))
    result = {
        "label": LABEL,
        "launcher_pid": process.pid if process else None,
        "worker_pid": worker_pid,
        "worker_reported_exit": worker_exit,
        "exit_code": process.returncode if process else None,
        "supervisor_failure": failure,
        "job_empty": job_empty,
        "worker_exited": process is not None and process.poll() is not None and job_empty,
        "device_after": asdict(after),
        "session_seconds": time.monotonic() - started,
    }
    (run_dir / "supervisor_result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2), flush=True)
    return 0 if process and process.returncode == 0 and worker_exit == 0 and not failure else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--authorize-repair1-pilot", action="store_true")
    group.add_argument("--authorize-final-language", action="store_true")
    group.add_argument("--authorize-internvl-pilot", action="store_true")
    group.add_argument("--authorize-capability-pilot", action="store_true")
    args = parser.parse_args()
    raise SystemExit(
        run(
            args.root.resolve(),
            True,
            final_language=args.authorize_final_language,
            internvl=args.authorize_internvl_pilot,
            capability=args.authorize_capability_pilot,
        )
    )
