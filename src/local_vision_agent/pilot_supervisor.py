"""Launch exactly one model worker, preserve evidence and enforce process deadlines."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .gpu_guard import query_gpu_snapshot
from .pilot_policy import LABEL, PilotLimits


def stop_process(process: subprocess.Popen[Any], timeout_s: float) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=timeout_s)


def windows_memory() -> dict[str, Any]:
    command = (
        "Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUProcessMemory | "
        "Select-Object Name,DedicatedUsage,SharedUsage,TotalCommitted | ConvertTo-Json -Depth 3"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "limitation": "Adapter LUID attribution and inter-sample spill may be unknown",
    }


def run(root: Path, authorized: bool) -> int:
    if not authorized:
        raise RuntimeError("Explicit --authorize-initial-pilot is required")
    limits = PilotLimits()
    run_dir = root / "runs" / "initial-pilot"
    # This exclusive creation persists even on failure: do not silently retry a model load.
    run_dir.mkdir(parents=True, exist_ok=False)
    project = Path(__file__).resolve().parents[2]
    git = ["git", "-c", f"safe.directory={project.as_posix()}"]

    def git_read(*args: str) -> str:
        return subprocess.run(
            [*git, *args], cwd=project, capture_output=True, text=True, check=True, timeout=10
        ).stdout.strip()

    metadata: dict[str, Any] = {
        "label": LABEL,
        "started": datetime.now().astimezone().isoformat(),
        "commit": git_read("rev-parse", "HEAD"),
        "dirty_state": git_read("status", "--porcelain"),
        "limits": asdict(limits),
        "source_hashes": {},
    }
    for path in (project / "src/local_vision_agent").glob("*.py"):
        metadata["source_hashes"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
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
    failure = None
    next_sample = started
    process = None
    try:
        with (
            (run_dir / "stdout.txt").open("w", encoding="utf8") as stdout,
            (run_dir / "stderr.txt").open("w", encoding="utf8") as stderr,
        ):
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "local_vision_agent.pilot_worker",
                    "--root",
                    str(root),
                    "--run-dir",
                    str(run_dir),
                ],
                cwd=project,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            last_phase = None
            while process.poll() is None:
                now = time.monotonic()
                status_path = run_dir / "status.json"
                status = (
                    json.loads(status_path.read_text(encoding="utf8"))
                    if status_path.exists()
                    else {}
                )
                phase = status.get("phase", "starting")
                if phase != last_phase:
                    print(phase, status.get("operation", ""), flush=True)
                    last_phase = phase
                # Entire load is bounded even if intermediate preflight events update status.
                events = (run_dir / "events.jsonl").read_text(encoding="utf8") if status else ""
                loaded = '"phase": "model_loaded"' in events
                if now - started > limits.session_s:
                    failure = "SESSION_TIMEOUT"
                elif not loaded and phase not in {
                    "failure",
                    "cleanup_start",
                    "cleanup_done",
                    "worker_done",
                }:
                    if now - started > limits.load_s:
                        failure = "LOAD_TIMEOUT"
                elif phase == "call_start" and now - status["monotonic"] > limits.call_s:
                    failure = "CALL_TIMEOUT"
                if "image_started" in status and now - status["image_started"] > limits.image_s:
                    failure = "IMAGE_TIMEOUT"
                if phase == "cleanup_start" and now - status["monotonic"] > limits.cleanup_s:
                    failure = "CLEANUP_TIMEOUT"
                if now >= next_sample:
                    sample = query_gpu_snapshot()
                    with (run_dir / "device_samples.jsonl").open("a") as handle:
                        handle.write(json.dumps({"monotonic": now, **asdict(sample)}) + "\n")
                    if sample.free_mib < limits.reserve_mib:
                        failure = "DEDICATED_FREE_RESERVE"
                    if sample.used_mib - before.used_mib > limits.ceiling_mib:
                        failure = "DEVICE_USAGE_CEILING"
                    next_sample = now + 0.5
                if failure:
                    stop_process(process, limits.cleanup_s / 2)
                    break
                time.sleep(0.05)
            process.wait(timeout=limits.cleanup_s)
    except Exception as exc:  # noqa: BLE001 -- supervisor must terminate worker on every error
        failure = f"SUPERVISOR_ERROR:{type(exc).__name__}:{exc}"
    finally:
        if process is not None:
            stop_process(process, limits.cleanup_s / 2)
    after = query_gpu_snapshot()
    (run_dir / "windows_after.json").write_text(json.dumps(windows_memory(), indent=2))
    processes = subprocess.run(
        ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    result = {
        "label": LABEL,
        "worker_pid": process.pid if process else None,
        "exit_code": process.returncode if process else None,
        "supervisor_failure": failure,
        "worker_exited": process is not None and process.poll() is not None,
        "device_after": asdict(after),
        "processes_after": processes.stdout,
        "session_seconds": time.monotonic() - started,
    }
    (run_dir / "supervisor_result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2), flush=True)
    return 0 if process and process.returncode == 0 and not failure else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--authorize-initial-pilot", action="store_true")
    args = parser.parse_args()
    raise SystemExit(run(args.root.resolve(), args.authorize_initial_pilot))
