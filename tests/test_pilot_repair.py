"""CPU-only regression checks for Windows supervision, cleanup and query templates."""

import ast
import io
import json
import os
import runpy
import subprocess
import sys
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from local_vision_agent.gpu_guard import GpuSnapshot
from local_vision_agent.pilot_cleanup import clear_workspaces
from local_vision_agent.pilot_ipc import Deadlines, EventReader
from local_vision_agent.pilot_policy import PilotLimits, PilotRefusal
from local_vision_agent.pilot_supervisor_repair import run as supervised_run
from local_vision_agent.pilot_worker import Evidence
from local_vision_agent.windows_job import WindowsJob


class RepairTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows supervisor integration")
    def test_supervisor_success_and_timeout_with_cpu_worker(self):
        real_popen = subprocess.Popen
        for timeout in (False, True):
            with self.subTest(timeout=timeout), tempfile.TemporaryDirectory() as directory:
                source = (
                    "import os,sys,json,time\n"
                    "def emit(phase,**extra):\n"
                    " print(json.dumps(dict(phase=phase,pid=os.getpid(),monotonic=time.monotonic(),**extra)),flush=True)\n"
                    "emit('ready')\nassert sys.stdin.readline().strip()=='GO'\n"
                    "emit('load_start')\nemit('model_loaded')\nemit('image_start')\nemit('call_start')\n"
                    + (
                        "time.sleep(30)\n"
                        if timeout
                        else "emit('call_done')\nemit('cleanup_start')\nemit('workspace_cleanup')\nemit('cleanup_done')\nemit('worker_done',exit_code=0)\n"
                    )
                )

                def launch(command, fixture=source, **kwargs):
                    if "local_vision_agent.pilot_worker" in command:
                        command = [sys.executable, "-B", "-c", fixture]
                    return real_popen(command, **kwargs)

                with (
                    patch(
                        "local_vision_agent.pilot_supervisor_repair.subprocess.Popen",
                        side_effect=launch,
                    ),
                    patch(
                        "local_vision_agent.pilot_supervisor_repair.query_gpu_snapshot",
                        return_value=GpuSnapshot("CPU fixture", 8192, 182, 7836),
                    ),
                    patch(
                        "local_vision_agent.pilot_supervisor_repair.windows_memory", return_value={}
                    ),
                    patch(
                        "local_vision_agent.pilot_supervisor_repair.PilotLimits",
                        return_value=replace(PilotLimits(), call_s=0.2, load_s=5, cleanup_s=2),
                    ),
                    patch("sys.stdout", io.StringIO()),
                ):
                    code = supervised_run(Path(directory), True)
                result = json.loads(
                    (Path(directory) / "runs/repair1-pilot/supervisor_result.json").read_text()
                )
                self.assertEqual(code, 1 if timeout else 0)
                self.assertTrue(result["job_empty"])
                self.assertTrue(result["worker_exited"])
                if timeout:
                    self.assertIn("CALL_TIMEOUT", result["supervisor_failure"])

    def test_pipe_preserves_large_unicode_events_without_status_file(self):
        with tempfile.TemporaryDirectory() as directory:
            stream = io.StringIO()
            with (
                patch("sys.stdout", stream),
                patch.object(Path, "replace", side_effect=PermissionError),
            ):
                evidence = Evidence(Path(directory), pipe=True)
                for i in range(20):
                    evidence.emit("test", number=i, payload="繁體中文" * 10000)
            reader = EventReader(io.StringIO(stream.getvalue()))
            for i in range(20):
                self.assertEqual(reader.receive(2)["number"], i)
            with self.assertRaises(EOFError):
                reader.receive(2)
            self.assertFalse((Path(directory) / "status.json").exists())
            self.assertEqual(
                len((Path(directory) / "events.jsonl").read_text(encoding="utf8").splitlines()), 20
            )

    def test_invalid_pipe_event_fails_closed(self):
        reader = EventReader(io.StringIO("not-json\n"))
        with self.assertRaises(PilotRefusal):
            reader.receive(2)

    def test_deadlines_do_not_reset_with_telemetry_or_cleanup_events(self):
        limits = PilotLimits()
        state = Deadlines(0, limits)
        state.observe({"phase": "cuda_baseline", "monotonic": 175})
        with self.assertRaisesRegex(PilotRefusal, "LOAD_TIMEOUT"):
            state.check(181)
        state = Deadlines(0, limits, loaded=True)
        state.observe({"phase": "image_start", "monotonic": 0})
        state.observe({"phase": "call_start", "monotonic": 10})
        with self.assertRaisesRegex(PilotRefusal, "CALL_TIMEOUT"):
            state.check(71)
        state.observe({"phase": "cleanup_start", "monotonic": 72})
        state.observe({"phase": "workspace_cleanup", "monotonic": 80})
        with self.assertRaisesRegex(PilotRefusal, "CLEANUP_TIMEOUT"):
            state.check(83)

    def test_late_call_result_is_not_accepted(self):
        state = Deadlines(0, PilotLimits(), loaded=True)
        state.observe({"phase": "call_start", "monotonic": 0})
        with self.assertRaises(PilotRefusal):
            state.observe({"phase": "call_done", "monotonic": 61})

    def test_workspace_cleanup_order_and_measurement(self):
        framework = Mock()
        framework.__version__ = "2.7.1+cu126"
        framework.cuda.memory_allocated.side_effect = [8519680, 0]
        result = clear_workspaces(framework)
        self.assertEqual(result["before_allocated_bytes"], 8519680)
        self.assertEqual(result["after_allocated_bytes"], 0)
        names = [call[0] for call in framework.mock_calls]
        self.assertLess(
            names.index("_C._cuda_clearCublasWorkspaces"), names.index("cuda.empty_cache")
        )
        framework._C._cuda_clearCublasWorkspaces = None
        framework.cuda.memory_allocated.side_effect = None
        framework.cuda.memory_allocated.return_value = 0
        with self.assertRaisesRegex(RuntimeError, "UNAVAILABLE"):
            clear_workspaces(framework)

    def test_worker_requires_handshake_without_importing_model(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "local_vision_agent.pilot_worker",
                "--root",
                "missing",
                "--run-dir",
                "missing",
                "--repair1",
            ],
            input="",
            text=True,
            encoding="utf8",
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["phase"], "ready")
        self.assertIn("HANDSHAKE_REQUIRED", result.stderr)

    @unittest.skipUnless(os.name == "nt", "Windows kernel regression")
    def test_job_terminates_actual_venv_worker_and_descendant(self):
        # The Windows venv launcher PID may differ from the real Python PID.
        source = (
            "import os,sys,subprocess,time; print(os.getpid(),flush=True); "
            "assert sys.stdin.readline().strip()=='GO'; "
            "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); "
            "print(child.pid,flush=True); time.sleep(60)"
        )
        process = subprocess.Popen(
            [sys.executable, "-B", "-c", source],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        job = WindowsJob()
        try:
            pid = int(process.stdout.readline())
            job.assign(pid)
            process.stdin.write("GO\n")
            process.stdin.flush()
            int(process.stdout.readline())
            deadline = time.monotonic() + 3
            while job.active_count() < 2 and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertGreaterEqual(job.active_count(), 2)
            job.terminate(3)
            self.assertEqual(job.active_count(), 0)
            process.wait(timeout=3)
        finally:
            job.close()
            if process.poll() is None:
                process.kill()
                process.wait(timeout=3)
            process.stdin.close()
            process.stdout.close()

    def test_query_patch_changes_only_second_suffix_with_fake_tensor_backend(self):
        project = Path(__file__).resolve().parents[1]
        patch_query = runpy.run_path(str(project / "scripts/phase2_prepare_repair.py"))[
            "patch_query"
        ]
        source_path = project / "artifacts/phase2-20260927/controlled/md2_fixed/moondream.py"
        if not source_path.exists():
            self.skipTest("Local pinned source is intentionally ignored")
        tree = ast.parse(patch_query(source_path.read_text(encoding="utf8")))
        cls = next(
            n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MoondreamModel"
        )
        query = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "query")
        module = ast.Module(
            body=[
                ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0),
                query,
            ],
            type_ignores=[],
        )
        namespace = {"torch": SimpleNamespace(tensor=lambda value, **kwargs: value)}
        exec(compile(ast.fix_missing_locations(module), "reviewed-query-only", "exec"), namespace)  # noqa: S102 -- isolated reviewed function, fake tensor backend
        captured = []
        model = SimpleNamespace(
            config=SimpleNamespace(
                tokenizer=SimpleNamespace(
                    templates={"query": {"prefix": [1, 15381, 2], "suffix": [3]}}
                )
            ),
            device="fake",
            attn_mask=None,
            tokenizer=SimpleNamespace(encode=lambda text: SimpleNamespace(ids=[42])),
            encode_image=lambda image, settings: SimpleNamespace(pos=730),
            load_encoded_image=lambda image: None,
            _generate_answer=lambda prompt, *args, **kwargs: captured.append(prompt) or ["test"],
        )
        for duplicate in (True, False):
            model._pilot_duplicate_query_suffix = duplicate
            namespace["query"](model, object(), "test", reasoning=False)
        self.assertEqual(captured, [[[1, 15381, 2, 42, 3, 3]], [[1, 15381, 2, 42, 3]]])


if __name__ == "__main__":
    unittest.main()
