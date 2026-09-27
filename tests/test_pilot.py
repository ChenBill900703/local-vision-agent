"""Safe CPU failure-path tests; never import/instantiate a GPU model."""

import subprocess
import sys
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from local_vision_agent.gpu_guard import GpuGuard, GpuSafetyError, GpuSnapshot, ModelMemorySpec
from local_vision_agent.pilot_policy import (
    PilotBudget,
    PilotLimits,
    PilotRefusal,
    hash_file,
    validate_image,
)
from local_vision_agent.pilot_supervisor import stop_process
from local_vision_agent.pilot_worker import run as worker_run


class PilotTests(unittest.TestCase):
    def test_provisional_estimate_refuses_insufficient_free(self):
        guard = GpuGuard()
        for free in (7535, 4000):
            with self.assertRaises(GpuSafetyError):
                guard.preflight(
                    ModelMemorySpec("UNMEASURED", 6000),
                    GpuSnapshot("test fixture", 8192, 8192 - free, free),
                )
        guard.preflight(
            ModelMemorySpec("UNMEASURED", 6000), GpuSnapshot("test fixture", 8192, 656, 7536)
        )

    def test_bounded_calls_and_tokens(self):
        budget = PilotBudget(PilotLimits())
        budget.start_image()
        for _ in range(8):
            budget.before_call(10, 128)
            budget.after_call(128)
        with self.assertRaises(PilotRefusal):
            budget.before_call(10, 128)
        budget.start_image()
        for args in ((1025, 1), (10, 129), (True, 1)):
            with self.assertRaises(PilotRefusal):
                budget.before_call(*args)
        with self.assertRaises(PilotRefusal):
            budget.after_call(129)

    def test_image_session_and_batch_limits(self):
        now = [0]
        budget = PilotBudget(PilotLimits(), clock=lambda: now[0])
        for _ in range(3):
            budget.start_image()
        with self.assertRaises(PilotRefusal):
            budget.start_image()
        now[0] = 301
        with self.assertRaisesRegex(PilotRefusal, "IMAGE_TIMEOUT"):
            budget.before_call()
        now[0] = 1801
        with self.assertRaisesRegex(PilotRefusal, "SESSION_TIMEOUT"):
            budget.before_call()

    def test_rejects_oversized_image_before_model(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.png"
            Image.new("RGB", (513, 2)).save(path)
            with self.assertRaisesRegex(PilotRefusal, "IMAGE_RESOLUTION"):
                validate_image(path, hash_file(path), PilotLimits())
            with self.assertRaisesRegex(PilotRefusal, "IMAGE_BYTES"):
                validate_image(path, hash_file(path), replace(PilotLimits(), max_bytes=1))
            with self.assertRaisesRegex(PilotRefusal, "IMAGE_HASH"):
                validate_image(path, "wrong", PilotLimits())

    def test_worker_termination_no_dangerous_oom(self):
        process = subprocess.Popen(
            [sys.executable, "-B", "-c", "import time; time.sleep(30)"],
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        start = time.monotonic()
        try:
            stop_process(process, 1)
            self.assertIsNotNone(process.poll())
            self.assertLess(time.monotonic() - start, 3)
        finally:
            stop_process(process, 1)

    def test_pilot_modules_do_not_import_framework(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                "import local_vision_agent.pilot_worker,sys; assert 'torch' not in sys.modules",
            ],
            capture_output=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_preflight_exception_records_failure_and_cleanup_without_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch("local_vision_agent.pilot_worker.validate_assets", return_value={}),
                patch("local_vision_agent.pilot_worker.deny_network"),
                patch(
                    "local_vision_agent.pilot_worker.GpuGuard.preflight",
                    side_effect=GpuSafetyError("synthetic insufficient VRAM"),
                ),
            ):
                self.assertEqual(worker_run(root, root), 1)
            text = (root / "events.jsonl").read_text(encoding="utf8")
            self.assertIn("synthetic insufficient VRAM", text)
            self.assertIn("cleanup_start", text)
            self.assertIn("worker_done", text)


if __name__ == "__main__":
    unittest.main()
