"""CPU/Fake/Qt evidence only. Never a physical camera or GPU model test."""

import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")

from PIL import Image
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication

from local_vision_agent.app_camera import FakeCamera, QtCamera
from local_vision_agent.app_controller import AppController, AppState, SessionLimits
from local_vision_agent.app_session import PersistentAnalysisSession
from local_vision_agent.app_storage import AppStorage
from local_vision_agent.app_worker import (
    AnalysisWorker,
    AppRequest,
    FakeAnalysisSession,
    inspect_capture,
    timestamp,
)
from local_vision_agent.contracts import AgentError, ImageInput
from local_vision_agent.gpu_guard import GpuSnapshot
from local_vision_agent.internvl_backend import InternVLBackend
from local_vision_agent.internvl_contract import load_runtime_config
from local_vision_agent.pilot_worker import Evidence
from local_vision_agent.windows_app import MainWindow

PROJECT = Path(__file__).resolve().parents[1]
APP = QApplication.instance() or QApplication([])


def spin(predicate, seconds=3):
    deadline = time.monotonic() + seconds
    while not predicate() and time.monotonic() < deadline:
        APP.processEvents()
        time.sleep(0.005)
    if not predicate():
        raise AssertionError("Qt event condition timed out")


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.c = AppController(lambda: self.now)

    def test_manual_selection_and_request(self):
        self.assertIsNone(self.c.request("IMAGE"))
        self.c.select_image()
        self.assertIsNotNone(self.c.request("IMAGE"))
        self.assertEqual(self.c.state, AppState.ANALYZING_IMAGE)

    def test_sequential_completion_then_interval(self):
        self.c.start_auto(SessionLimits())
        first = self.c.request("WEBCAM")
        self.now = 12
        self.assertIsNone(self.c.request("WEBCAM"))
        self.c.complete(first, True)
        self.assertEqual(self.c.next_due, 17)
        self.now = 16.99
        self.assertIsNone(self.c.request("WEBCAM"))
        self.now = 17
        self.assertIsNotNone(self.c.request("WEBCAM"))

    def test_interval_validation(self):
        for value in [0, -1, 2, 31, True, 3.5, float("inf")]:
            with self.assertRaises(ValueError):
                SessionLimits(interval_s=value)
        for value in [3, 5, 30]:
            self.assertEqual(SessionLimits(interval_s=value).interval_s, value)

    def test_no_queue_and_manual_disabled_during_auto(self):
        self.c.start_auto(SessionLimits())
        self.assertIsNone(self.c.request("IMAGE"))
        first = self.c.request("WEBCAM")
        for _ in range(20):
            self.assertIsNone(self.c.request("WEBCAM"))
        self.assertEqual(self.c.pending, first)
        self.assertEqual(self.c.frame_count, 1)

    def test_unique_sessions_and_frames(self):
        ids = set()
        for _ in range(4):
            self.c.recover()
            self.c.start_auto(SessionLimits())
            identifier = self.c.request("WEBCAM")
            ids.add(identifier)
            self.c.complete(identifier, True)
            self.now += 5
            identifier = self.c.request("WEBCAM")
            ids.add(identifier)
            self.c.complete(identifier, True)
            self.c.stop()
        self.assertEqual(len(ids), 8)

    def test_stale_callback_does_not_release_busy(self):
        self.c.start_auto(SessionLimits())
        identifier = self.c.request("WEBCAM")
        self.assertFalse(self.c.complete("old-frame", True))
        self.assertTrue(self.c.busy)
        self.assertEqual(self.c.pending, identifier)

    def test_max_frame_limit(self):
        self.c.start_auto(SessionLimits(max_frames=2))
        for _ in range(2):
            identifier = self.c.request("WEBCAM")
            self.c.complete(identifier, True)
            self.now += 5
        self.assertIsNone(self.c.request("WEBCAM"))
        self.assertFalse(self.c.auto)

    def test_max_duration_includes_busy_time(self):
        self.c.start_auto(SessionLimits(max_duration_s=10))
        identifier = self.c.request("WEBCAM")
        self.now = 11
        self.c.complete(identifier, True)
        self.assertIsNone(self.c.request("WEBCAM"))

    def test_stop_idle(self):
        self.c.stop()
        self.assertEqual(self.c.state, AppState.IDLE)
        self.assertIsNone(self.c.request("WEBCAM"))

    def test_stop_active_drains_without_new_work(self):
        self.c.start_auto(SessionLimits())
        identifier = self.c.request("WEBCAM")
        self.c.stop()
        self.assertTrue(self.c.busy)
        self.assertEqual(self.c.state, AppState.STOPPING)
        self.c.complete(identifier, True)
        self.assertIsNone(self.c.request("WEBCAM"))
        self.assertFalse(self.c.busy)

    def test_error_recovery_and_close(self):
        self.c.select_image()
        self.c.complete(self.c.request("IMAGE"), False)
        self.assertEqual(self.c.state, AppState.ERROR)
        self.c.recover()
        self.c.select_image()
        self.c.close()
        self.assertIsNone(self.c.request("IMAGE"))


class StorageAndSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.storage = AppStorage(self.root / "app")
        self.config = load_runtime_config(PROJECT / "configs/agent_internvl_development.toml")
        self.path = self.root / "original.png"
        Image.new("RGB", (16, 16), "white").save(self.path)

    def test_history_roundtrip_and_corrupt_record(self):
        d = self.storage.allocate("record-1")
        data = {
            "schema": "windows-app-result-v1",
            "report_text": "<script>文字</script>",
            "metadata": {"status": "failed"},
        }
        self.storage.save(d, data)
        self.assertEqual(self.storage.load("record-1/result.json"), data)
        (self.storage.allocate("record-2") / "result.json").write_text("{")
        self.assertEqual(len(self.storage.history()), 2)
        self.assertEqual(sum(x[1] is None for x in self.storage.history()), 1)

    def test_storage_escape_and_user_file_preservation(self):
        for path in ["../original.png", str(self.path)]:
            with self.assertRaises(ValueError):
                self.storage.path(path)
        with self.assertRaises(ValueError):
            self.storage.remove_frame(self.root)
        self.assertTrue(self.path.exists())

    def _worker(self, save):
        d = self.storage.allocate("frame-save-" + str(save))
        frame = d / "frame.png"
        Image.new("RGB", (1000, 750), "blue").save(frame)
        self.storage.save(d, inspect_capture(frame), "capture.json")
        worker = AnalysisWorker(FakeAnalysisSession(self.config), self.storage, self.config)
        results = []
        worker.result.connect(lambda _id, data: results.append(data))
        worker.analyze(AppRequest(d.name, "WEBCAM", frame, d, timestamp(), "session-test", save))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["metadata"]["status"], "complete")
        self.assertEqual(results[0]["metadata"]["capture"]["width"], 1000)
        self.assertIsNone(results[0]["metadata"]["allocated_mib"])
        return d, worker

    def test_frame_save_off_removes_source_and_normalized(self):
        d, _ = self._worker(False)
        self.assertFalse((d / "frame.png").exists())
        self.assertFalse((d / "input/normalized.png").exists())
        self.assertTrue((d / "result.json").exists())

    def test_frame_save_on_retains_only_analyzed(self):
        d, _ = self._worker(True)
        self.assertTrue((d / "frame.png").exists())
        self.assertTrue((d / "input/normalized.png").exists())

    def test_abandoned_ephemeral_cleanup_preserves_saved(self):
        for save in [False, True]:
            d = self.storage.allocate("abandoned-" + str(save))
            (d / "frame.png").write_bytes(b"fixture")
            self.storage.save(d, {"save_frame": save}, "retention.json")
        self.storage.purge_ephemeral()
        self.assertFalse(self.storage.path("abandoned-False/frame.png").exists())
        self.assertTrue(self.storage.path("abandoned-True/frame.png").exists())

    def test_invalid_image_failure_history_and_no_load(self):
        d = self.storage.allocate("invalid-image")
        session = PersistentAnalysisSession(self.root, self.root / "runtime", self.config)
        worker = AnalysisWorker(session, self.storage, self.config)
        with patch.object(session.adapter, "load") as load:
            worker.analyze(
                AppRequest("invalid-image", "IMAGE", self.root / "missing", d, timestamp(), "s")
            )
            load.assert_not_called()
        self.assertEqual(
            self.storage.load("invalid-image/result.json")["metadata"]["status"], "failed"
        )

    def test_persistent_session_one_load_no_cross_frame_state(self):
        session = PersistentAnalysisSession(self.root, self.root / "runtime", self.config)
        adapter = session.adapter
        active = {"id": None, "calls": 0, "ends": 0}

        def load():
            adapter.loaded = True
            return {}

        def request(op, payload, timeout):
            if op == "begin_image":
                from dataclasses import asdict

                from local_vision_agent.image_input import inspect_image

                active["id"] = payload["input_id"]
                active["calls"] = 0
                info = inspect_image(
                    ImageInput(active["id"], Path(payload["path"])), self.config.limits
                )
                return {
                    "image": asdict(info),
                    "tile_count": 1,
                    "preprocessing": self.config.preprocessing,
                }
            if op == "end_image":
                active["id"] = None
                active["calls"] = 0
                active["ends"] += 1
                return {"image_cleared": True}
            active["calls"] += 1
            raw = "supported" if payload["prompt_id"] == "verify" else str(active["id"]) + "。"
            return {
                "raw_response": raw,
                "output_tokens": 2,
                "stop_reason": "eos",
                "latency_s": 0.01,
                "call_id": f"call-{active['calls']}",
                "input_id": active["id"],
            }

        with (
            patch.object(adapter, "load", side_effect=load) as loader,
            patch.object(adapter.transport, "request", side_effect=request),
        ):
            reports = [
                session.analyze(ImageInput(f"frame-{i}", self.path), self.root / f"input-{i}")
                for i in range(3)
            ]
        self.assertEqual(loader.call_count, 1)
        self.assertEqual(active["ends"], 3)
        self.assertIsNone(adapter.image)
        self.assertEqual(adapter.trace, [])
        for i, r in enumerate(reports):
            self.assertEqual(r.observations[0].call_id, "call-1")
            self.assertEqual(r.candidate_claim_count, 1)
            self.assertEqual(r.verification_completed, 1)
            self.assertEqual(r.claims[0].text, f"frame-{i}")
            for j in range(3):
                if i != j:
                    self.assertNotIn(f"frame-{j}", str(r))
            self.assertIn(f"input=frame-{i}", str(r.runtime_metadata["observation_evidence"]))
        with patch.object(adapter, "unload", return_value={"worker_exited": True}) as unload:
            self.assertTrue(session.close()["worker_exited"])
            session.close()
            unload.assert_called_once()

    def test_backend_reset_retains_model_session_and_clears_image_counters(self):
        (self.root / "evidence").mkdir()
        backend = InternVLBackend(self.root, self.config, Evidence(self.root / "evidence"))
        backend.persistent_images = True
        backend.model = object()
        model = backend.model
        backend.loaded_once = True
        backend.started = 123
        backend.image = object()
        backend.pixels = object()
        backend.image_id = "frame-a"
        backend.calls = 8
        backend.output_tokens = 1024
        backend.image_started = 150
        backend.torch = MagicMock()
        with patch("local_vision_agent.internvl_backend.measure", return_value={}):
            result = backend.end_image()
        self.assertTrue(result["image_cleared"])
        self.assertIs(backend.model, model)
        self.assertEqual(backend.started, 123)
        self.assertEqual((backend.calls, backend.output_tokens, backend.image_started), (0, 0, 0))
        self.assertIsNone(backend.image)
        self.assertIsNone(backend.pixels)
        self.assertTrue(backend.loaded_once)

    def test_legacy_reset_refused(self):
        backend = InternVLBackend(self.root, self.config, Evidence(self.root / "legacy"))
        with self.assertRaisesRegex(AgentError, "RESET_NOT_ALLOWED"):
            backend.end_image()

    def test_failed_reset_poisoned_no_retry(self):
        session = PersistentAnalysisSession(self.root, self.root / "runtime", self.config)
        adapter = session.adapter
        adapter.loaded = True
        adapter.image = object()
        with (
            patch.object(adapter.transport, "request", return_value={"image_cleared": False}),
            patch.object(adapter.transport, "abort") as abort,
        ):
            with self.assertRaisesRegex(AgentError, "RESET_UNVERIFIED"):
                adapter.end_image()
            self.assertTrue(adapter.failed)
            abort.assert_called_once()

    def test_worker_cleanup_failure_is_persisted(self):
        session = MagicMock()
        session.close.side_effect = RuntimeError("cleanup failed")
        worker = AnalysisWorker(session, self.storage, self.config)
        results = []
        worker.closed.connect(results.append)
        worker.close()
        worker.close()
        session.close.assert_called_once()
        self.assertIn("cleanup_error", results[0])
        self.assertEqual(len(list(self.storage.root.glob("*/cleanup.json"))), 1)

    @unittest.skipUnless(os.name == "nt", "Windows supervised CPU child fixture")
    def test_three_images_through_persistent_rpc_one_process(self):
        from test_internvl_adapter import fixture_source

        script = fixture_source("clear")
        script = script.replace(
            "a=parser.parse_args()",
            "parser.add_argument('--persistent-images',action='store_true');a=parser.parse_args()",
        )
        script = script.replace("if op=='begin_image':", "if op=='begin_image':\n  count=0")
        script = script.replace(
            "elif op=='unload':",
            "elif op=='end_image':\n  count=0\n  reply(r['id'],op,dict(image_cleared=True))\n elif op=='unload':",
        )
        popen = subprocess.Popen

        def launch(command, **kwargs):
            if "local_vision_agent.internvl_rpc_worker" not in command:
                return popen(command, **kwargs)
            start = command.index("local_vision_agent.internvl_rpc_worker")
            return popen([sys.executable, "-B", "-c", script, *command[start + 1 :]], **kwargs)

        session = PersistentAnalysisSession(self.root, self.root / "rpc", self.config)
        snapshot = GpuSnapshot("CPU FIXTURE", 8192, 200, 7800)
        with (
            patch(
                "local_vision_agent.internvl_transport.subprocess.Popen", side_effect=launch
            ) as launches,
            patch(
                "local_vision_agent.internvl_transport.query_gpu_snapshot", return_value=snapshot
            ),
            patch(
                "local_vision_agent.pilot_supervisor_repair.query_gpu_snapshot",
                return_value=snapshot,
            ),
        ):
            try:
                pids = []
                for i in range(3):
                    report = session.analyze(
                        ImageInput(f"rpc-frame-{i}", self.path), self.root / f"rpc-input-{i}"
                    )
                    self.assertEqual(report.status, "complete")
                    self.assertEqual(report.observations[0].call_id, "call-1")
                    self.assertEqual(session.adapter.transport.image_deadline, 0)
                    pids.append(session.adapter.transport.worker_pid)
                self.assertEqual(len(set(pids)), 1)
                self.assertEqual(
                    sum(
                        "local_vision_agent.internvl_rpc_worker" in call.args[0]
                        for call in launches.call_args_list
                    ),
                    1,
                )
                self.assertTrue(session.close()["job_empty"])
                self.assertEqual(session.adapter.transport.process.returncode, 0)
            finally:
                session.adapter.transport.abort()

    def test_application_error_variants_preserve_failure_and_private_frames(self):
        for error in ["GPU_BUDGET", "OOM", "TOOL_TIMEOUT", "RPC_RESPONSE_MISMATCH", "LOAD_TIMEOUT"]:
            d = self.storage.allocate("failure-" + error.replace("_", "-"))
            image = d / "frame.png"
            Image.new("RGB", (16, 16)).save(image)
            session = MagicMock()
            session.analyze.side_effect = AgentError(error)
            worker = AnalysisWorker(session, self.storage, self.config)
            worker.analyze(AppRequest(d.name, "WEBCAM", image, d, timestamp(), "test", False))
            result = self.storage.load(str(d.relative_to(self.storage.root) / "result.json"))
            self.assertEqual(result["metadata"]["status"], "failed")
            self.assertIn(error, result["report_text"])
            self.assertFalse(image.exists())
            session.analyze.assert_called_once()

    def test_real_rpc_dispatches_three_boundaries_without_second_load(self):
        from dataclasses import asdict

        from local_vision_agent.internvl_rpc_worker import serve

        directory = self.root / "rpc-dispatch"
        directory.mkdir()
        configuration = directory / "config.json"
        configuration.write_text(json.dumps(asdict(self.config)), encoding="utf-8")
        requests = []
        for i in range(3):
            requests.extend(
                [
                    {
                        "op": "begin_image",
                        "payload": {
                            "input_id": f"f-{i}",
                            "path": str(self.path),
                            "sha256": "fixture",
                        },
                    },
                    {"op": "end_image", "payload": {}},
                ]
            )
        requests.append({"op": "unload", "payload": {}})
        stream = io.StringIO(
            "".join(json.dumps({"id": i + 1, **r}) + "\n" for i, r in enumerate(requests))
        )
        backend = MagicMock()
        for name in ["load", "begin_image", "end_image", "unload"]:
            getattr(backend, name).return_value = {}
        with (
            patch("local_vision_agent.internvl_rpc_worker.InternVLBackend", return_value=backend),
            patch("sys.stdin", stream),
            patch("sys.stdout", io.StringIO()),
        ):
            self.assertEqual(serve(self.root, directory, configuration, persistent_images=True), 0)
        backend.load.assert_called_once()
        backend.unload.assert_called_once()
        self.assertEqual(backend.begin_image.call_count, 3)
        self.assertEqual(backend.end_image.call_count, 3)
        self.assertTrue(backend.persistent_images)

    def test_cleanup_failure_remains_visible_on_repeated_close(self):
        session = PersistentAnalysisSession(self.root, self.root / "runtime", self.config)
        session.adapter.loaded = True
        with patch.object(
            session.adapter, "unload", side_effect=RuntimeError("CLEANUP_FAILED")
        ) as unload:
            with self.assertRaises(RuntimeError):
                session.close()
            self.assertEqual(session.close(), {"cleanup_error": "CLEANUP_FAILED"})
            unload.assert_called_once()


class QtFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.config = load_runtime_config(PROJECT / "configs/agent_internvl_development.toml")
        self.storage = AppStorage(self.root / "app")
        self.camera = FakeCamera()
        self.session = FakeAnalysisSession(self.config)
        self.window = MainWindow(
            self.session, self.storage, self.config, camera=self.camera, demo=True
        )
        self.path = self.root / "photo.png"
        Image.new("RGB", (100, 80), "red").save(self.path)

    def tearDown(self):
        self.window.close()
        spin(lambda: self.window.shutdown_done)
        self.assertFalse(self.window.analysis_thread.isRunning())
        self.tmp.cleanup()

    def test_framework_import_no_cuda(self):
        import PySide6

        self.assertEqual(PySide6.__version__, "6.8.3")
        import torch

        self.assertFalse(torch.cuda.is_initialized())

    def test_fake_enumeration_open_capture_close(self):
        self.assertEqual(len(self.camera.devices()), 1)
        self.camera.open(0)
        frames = []
        self.camera.frame.connect(lambda i, x: frames.append((i, x)))
        self.camera.capture("one")
        spin(lambda: len(frames) == 1)
        self.assertEqual(frames[0][0], "one")
        self.camera.close()
        self.assertFalse(self.camera.opened)

    def test_camera_unavailable_disconnect_read_failure(self):
        with self.assertRaisesRegex(RuntimeError, "UNAVAILABLE"):
            self.camera.open(9)
        with self.assertRaisesRegex(RuntimeError, "DISCONNECTED"):
            self.camera.capture("a")
        self.camera.open(0)
        self.camera.failure = "CAMERA_READ_FAILED"
        with self.assertRaisesRegex(RuntimeError, "READ_FAILED"):
            self.camera.capture("b")

    def test_manual_preview_worker_result_and_history(self):
        self.window.select_path(self.path)
        spin(lambda: self.window.selected is not None)
        self.assertEqual(self.window.worker.thread(), self.window.analysis_thread)
        self.assertNotEqual(self.window.worker.thread(), QThread.currentThread())
        self.window.analyze_manual()
        spin(lambda: len(self.storage.history()) == 1)
        spin(lambda: not self.window.controller.busy)
        self.assertIn("CPU模擬", self.window.output.toPlainText())
        self.assertIn("N/A", self.window.output.toPlainText())
        self.window._history_selected(0, 0)
        self.assertEqual(len(self.storage.history()), 1)

    def test_invalid_preview_recovers(self):
        self.window.select_path(self.root / "missing.png")
        spin(lambda: self.window.preview_id is None)
        self.assertEqual(self.window.controller.state, AppState.ERROR)
        self.window.select_path(self.path)
        spin(lambda: self.window.selected is not None)

    def test_fake_auto_one_frame_no_capture_during_wait(self):
        self.window._open_camera()
        self.window._start_auto()
        spin(lambda: len(self.storage.history()) == 1)
        spin(lambda: not self.window.controller.busy)
        self.window._tick()
        self.assertEqual(self.camera.captures, 1)
        self.window.stop_webcam()
        self.assertFalse(self.camera.opened)
        self.assertFalse(self.window.controller.auto)

    def test_capture_error_stops_and_logs(self):
        self.window._open_camera()
        self.camera.failure = "CAMERA_READ_FAILED"
        self.window._start_auto()
        self.assertFalse(self.window.controller.auto)
        self.assertFalse(self.window.controller.busy)
        self.assertEqual(len(list(self.storage.root.glob("*/error.json"))), 1)

    def test_stale_frame_not_saved(self):
        from PySide6.QtGui import QImage

        self.window._frame("stale", QImage(8, 8, QImage.Format.Format_RGB32))
        self.assertFalse(list(self.storage.root.glob("*/frame.png")))

    def test_close_during_analysis_drains_and_releases(self):
        original = self.session.analyze

        def slow(*args):
            time.sleep(0.15)
            return original(*args)

        with patch.object(self.session, "analyze", side_effect=slow):
            self.window.select_path(self.path)
            spin(lambda: self.window.selected is not None)
            self.window.analyze_manual()
            self.window.close()
            self.assertFalse(self.window.shutdown_done)
            spin(lambda: self.window.shutdown_done)
        self.assertTrue(self.session.closed)
        self.assertEqual(len(self.storage.history()), 1)

    def test_qt_camera_enumeration_stub_no_physical_access(self):
        with patch("local_vision_agent.app_camera.QMediaDevices.videoInputs", return_value=[]):
            camera = QtCamera(self.window.video_preview)
            self.assertEqual(camera.devices(), [])
            with self.assertRaisesRegex(RuntimeError, "UNAVAILABLE"):
                camera.open(0)
            camera.close()

    def test_prospective_three_frame_limit_reaches_controller(self):
        self.window.session_limits = SessionLimits(max_frames=3)
        self.window._open_camera()
        self.window._start_auto()
        self.assertEqual(self.window.controller.limits.max_frames, 3)
        self.window.stop_webcam()

    def test_storage_failure_rejects_manual_before_analysis(self):
        self.window.select_path(self.path)
        spin(lambda: self.window.selected is not None)
        with patch.object(self.storage, "allocate", side_effect=OSError("disk full")):
            self.window.analyze_manual()
        self.assertFalse(self.window.controller.busy)
        self.assertIn("LOCAL_STORAGE_FAILED", self.window.status.text())
        self.assertEqual(len(self.storage.history()), 0)

    def test_storage_failure_stops_camera_without_capture(self):
        self.window._open_camera()
        with patch.object(self.storage, "allocate", side_effect=OSError("disk full")):
            self.window._start_auto()
        self.assertFalse(self.window.controller.busy)
        self.assertFalse(self.window.controller.auto)
        self.assertFalse(self.camera.opened)
        self.assertEqual(self.camera.captures, 0)
        self.assertIn("ERROR_LOG_WRITE_FAILED", self.window.status.text())

    def test_chinese_font_and_exclusive_storage(self):
        self.assertIn("JhengHei", self.window.font().family())
        with self.assertRaisesRegex(RuntimeError, "ALREADY_IN_USE"):
            MainWindow(self.session, self.storage, self.config, camera=FakeCamera(), demo=True)


if __name__ == "__main__":
    unittest.main()
