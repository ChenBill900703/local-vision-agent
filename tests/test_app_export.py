"""CPU-only export/review/session regressions. Fixture REAL labels test parsing, not GPUs."""

import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QByteArray
from PySide6.QtGui import QImage
from test_windows_app import QtFlowTests, spin

from local_vision_agent.app_camera import FakeCamera, QtCamera
from local_vision_agent.app_controller import SessionLimits
from local_vision_agent.app_export import (
    REAL,
    analysis_row,
    call_rows,
    cleanup_status,
    csv_text,
    engineering_summary,
    export_bundle,
    session_row,
    sheet_cell,
)
from local_vision_agent.app_export_schema import CALL_COLUMNS, SESSION_COLUMNS, SUMMARY_COLUMNS
from local_vision_agent.app_receipts import read_frame_receipts
from local_vision_agent.app_storage import AppStorage
from local_vision_agent.app_webcam_record import WebcamRecord


def fixture(identifier="frame-1", status="complete", real=False):
    return {
        "schema": "windows-app-result-v1",
        "report_text": '=圖片,「繁體中文」\r\n"原始回答"',
        "metadata": {
            "input_id": identifier,
            "session_id": "session-test",
            "source": "WEBCAM",
            "timestamp": "2026-10-01T00:00:00+00:00",
            "status": status,
            "analysis_latency_s": 2,
            "latency_s": 3,
            "allocated_mib": 0,
            "reserved_mib": 100,
            "device_used_mib": 200,
            "evidence_kind": REAL if real else "MOCK_NOT_RESEARCH_EVIDENCE",
        },
        "report": {
            "status": status,
            "completion": "COMPLETED",
            "stop_reason": "COMPLETED",
            "states": ["INITIAL_CAPTION", "VERIFICATION", "REPORT", "STOP"],
            "candidate_claim_count": 2,
            "verification_attempted": 1,
            "verification_completed": 1,
            "verification_unresolved_by_budget": 1,
            "verification_coverage_ratio": 0.5,
            "claims": [
                {"text": "紅色方形", "status": "supported", "verification_id": "call-2"},
                {"text": "背景", "status": "unresolved", "verification_id": None},
            ],
            "observations": [
                {
                    "call_id": "call-1",
                    "state": "INITIAL_CAPTION",
                    "request": {"tool": "caption", "prompt_id": "caption-v1", "claim": None},
                    "answer": {
                        "text": "紅色方形",
                        "output_tokens": 5,
                        "generation_stop_reason": "token_limit",
                        "truncated": True,
                    },
                },
                {
                    "call_id": "call-2",
                    "state": "VERIFICATION",
                    "request": {"tool": "verify", "prompt_id": "verify-v1", "claim": "紅色方形"},
                    "answer": {
                        "text": "supported",
                        "output_tokens": 1,
                        "generation_stop_reason": "eos",
                        "truncated": False,
                        "verdict": "supported",
                    },
                },
            ],
            "runtime_metadata": {
                "source_input": {
                    "source_width": 100,
                    "source_height": 80,
                    "source_format": "PNG",
                    "source_bytes": 321,
                    "source_sha256": "original",
                    "model_input": {"width": 100, "height": 80, "sha256": "normalized"},
                },
                "frame_trace": [
                    {
                        "call_id": "call-1",
                        "input_tokens": 10,
                        "output_tokens": 5,
                        "latency_s": 0.5,
                        "raw_response": "紅色方形",
                        "stop_reason": "token_limit",
                    },
                    {
                        "call_id": "call-2",
                        "input_tokens": 11,
                        "output_tokens": 1,
                        "latency_s": 0.25,
                        "raw_response": "supported",
                        "stop_reason": "eos",
                    },
                ],
                "calls_complete": True,
            },
        },
    }


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = AppStorage(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def save(self, data):
        directory = self.storage.allocate(data["metadata"]["input_id"])
        return str(self.storage.save(directory, data).relative_to(self.storage.root))

    def read_csv(self, path):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_exact_summary_column_contract(self):
        self.assertEqual(len(SUMMARY_COLUMNS), 43)
        self.assertEqual(
            SUMMARY_COLUMNS[:6],
            (
                "record_schema_version",
                "timestamp",
                "source_type",
                "session_id",
                "frame_id",
                "input_id",
            ),
        )
        self.assertEqual(
            SUMMARY_COLUMNS[-6:],
            (
                "human_rating",
                "human_note",
                "human_review_timestamp",
                "final_report",
                "error_type",
                "error_message",
            ),
        )
        self.save(fixture())
        out = export_bundle(self.storage)
        with (out / "analysis_summary.csv").open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(tuple(next(csv.reader(stream))), SUMMARY_COLUMNS)
        self.assertEqual(len(CALL_COLUMNS), 16)
        self.assertEqual(SESSION_COLUMNS[-1], "camera_backend_type")

    def test_formula_injection_all_prefixes(self):
        for prefix in "=+-@":
            with self.subTest(prefix=prefix):
                raw = prefix + 'HYPERLINK("x","繁體")'
                self.assertEqual(sheet_cell(raw), "'" + raw)
                self.assertEqual(sheet_cell(" \t\r\n" + raw), "' \t\r\n" + raw)

    def test_csv_quotes_commas_crlf_chinese_empty(self):
        raw = '繁體中文,"引號"\r\n第二行\n第三行'
        output = csv_text(("text", "empty", "zero"), [{"text": raw, "empty": None, "zero": 0}])
        parsed = list(csv.reader(io.StringIO(output, newline="")))
        self.assertEqual(parsed[1], [raw, "", "0"])

    def test_export_bytes_deterministic_and_canonical_unchanged(self):
        ref = self.save(fixture())
        before = self.storage.path(ref).read_bytes()
        a = export_bundle(self.storage)
        b = export_bundle(self.storage)
        for name in (
            "analysis_summary.csv",
            "model_calls.csv",
            "webcam_sessions.csv",
            "engineering_summary.json",
        ):
            self.assertEqual((a / name).read_bytes(), (b / name).read_bytes())
        self.assertEqual(self.storage.path(ref).read_bytes(), before)
        row = self.read_csv(a / "analysis_summary.csv")[0]
        self.assertEqual(row["final_report"], "'" + fixture()["report_text"])
        self.assertEqual(row["peak_allocated_mib"], "")
        self.assertEqual(row["normalized_sha256"], "normalized")

    def test_timestamp_id_row_order(self):
        z = fixture("z")
        z["metadata"]["timestamp"] = "2026-09-30T00:00:00+00:00"
        self.save(fixture("a"))
        self.save(z)
        rows = self.read_csv(export_bundle(self.storage) / "analysis_summary.csv")
        self.assertEqual([x["input_id"] for x in rows], ["z", "a"])

    def test_actual_calls_only_no_unvisited_or_budget_rows(self):
        data = fixture(real=True)
        data["report"]["states"].insert(1, "DETAIL_QUERY")
        rows = call_rows(data)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]["candidate_id"], "claim-1")
        self.assertEqual(rows[1]["verification_model_verdict"], "supported")
        self.assertEqual(rows[1]["verification_candidate_text"], "紅色方形")
        self.assertNotIn("DETAIL_QUERY", [x["agent_state"] for x in rows])
        summary = analysis_row(data)
        self.assertEqual(summary["verification_budget_unresolved"], 1)
        self.assertEqual(summary["total_tokens"], 27)

    def test_real_zero_vs_missing_measurement(self):
        data = fixture(real=True)
        self.assertEqual(analysis_row(data)["peak_allocated_mib"], 0)
        del data["metadata"]["allocated_mib"]
        self.assertIsNone(analysis_row(data)["peak_allocated_mib"])
        data["report"]["runtime_metadata"].pop("frame_trace")
        data["report"]["runtime_metadata"].pop("calls_complete")
        self.assertIsNone(analysis_row(data)["model_calls"])

    def test_mock_gpu_always_na_and_tokens_not_tokenized(self):
        row = analysis_row(fixture())
        self.assertTrue(row["record_schema_version"].endswith("MOCK"))
        self.assertIsNone(row["peak_allocated_mib"])
        self.assertIsNone(row["peak_reserved_mib"])
        self.assertIsNone(row["peak_device_used_mib"])
        self.assertIsNone(row["input_tokens"])
        self.assertEqual(row["output_tokens"], 6)

    def test_review_atomic_separate_raw_status_unchanged(self):
        ref = self.save(fixture())
        before = self.storage.path(ref).read_bytes()
        self.assertEqual(self.storage.review(ref)["human_rating"], "NOT_REVIEWED")
        updated = self.storage.update_review(ref, "PARTIALLY_USABLE", "部分可用\n保留錯誤")
        self.assertIsNotNone(updated["human_review_timestamp"])
        self.assertFalse(updated["ground_truth"])
        self.assertEqual(self.storage.review(ref)["human_note"], "部分可用\n保留錯誤")
        self.assertEqual(self.storage.path(ref).read_bytes(), before)
        row = self.read_csv(export_bundle(self.storage) / "analysis_summary.csv")[0]
        self.assertEqual(row["human_rating"], "PARTIALLY_USABLE")
        self.assertEqual(row["status"], "complete")

    def test_review_rejects_invalid_rating_and_path(self):
        ref = self.save(fixture())
        with self.assertRaises(ValueError):
            self.storage.update_review(ref, "ACCURATE", "x")
        with self.assertRaises(ValueError):
            self.storage.update_review("../outside.json", "USABLE", "x")
        self.assertFalse(list(self.storage.root.rglob("*.tmp")))

    def test_review_replace_failure_preserves_previous(self):
        ref = self.save(fixture())
        self.storage.update_review(ref, "USABLE", "before")
        with patch.object(Path, "replace", side_effect=OSError("disk")), self.assertRaises(OSError):
            self.storage.update_review(ref, "UNUSABLE", "after")
        self.assertEqual(self.storage.review(ref)["human_note"], "before")

    def test_corrupt_history_audited_not_crash(self):
        self.save(fixture())
        (self.storage.allocate("bad") / "result.json").write_text("not json")
        out = export_bundle(self.storage)
        audit = json.loads((out / "export_audit.json").read_text())
        self.assertTrue(any(x["error"] == "CORRUPT_HISTORY" for x in audit["errors"]))
        self.assertEqual(len(self.read_csv(out / "analysis_summary.csv")), 1)

    def test_corrupt_review_does_not_drop_valid_analysis(self):
        ref = self.save(fixture())
        self.storage.path(str(Path(ref).parent / "review.json")).write_text("bad")
        out = export_bundle(self.storage)
        self.assertEqual(len(self.read_csv(out / "analysis_summary.csv")), 1)
        self.assertIn("INVALID_REVIEW", (out / "export_audit.json").read_text())

    def test_empty_export_headers_and_unavailable_rates(self):
        out = export_bundle(self.storage)
        self.assertEqual(self.read_csv(out / "analysis_summary.csv"), [])
        summary = json.loads((out / "engineering_summary.json").read_text())
        self.assertEqual(summary["total_analysis_attempts"], 0)
        self.assertIsNone(summary["completion_rate"])
        self.assertIsNone(summary["mean_model_calls"])
        self.assertIsNone(summary["truncation_rate"])

    def test_safe_export_selection_and_paths(self):
        with self.assertRaises(ValueError):
            export_bundle(self.storage, "../outside")
        out = export_bundle(self.storage, "model_calls")
        self.assertTrue(out.resolve().is_relative_to(self.storage.root))
        self.assertTrue((out / "model_calls.csv").exists())
        self.assertFalse((out / "analysis_summary.csv").exists())

    def test_summary_denominators_missing_and_real_only_gpu(self):
        a = analysis_row(fixture(real=True))
        b = analysis_row(fixture("b", "failed"))
        b["model_calls"] = None
        c = analysis_row(fixture("c", "partial"))
        c["human_rating"] = "USABLE"
        result = engineering_summary([a, b, c])
        self.assertEqual(
            (result["complete_count"], result["partial_count"], result["failed_count"]), (1, 1, 1)
        )
        self.assertAlmostEqual(result["completion_rate"], 1 / 3)
        self.assertEqual(result["usable_count"], 1)
        self.assertIsNone(result["total_model_calls"])
        self.assertEqual(result["model_calls_known_count"], 2)
        self.assertEqual(result["mean_model_calls"], 2)
        self.assertEqual(result["number_with_real_gpu_measurement"], 1)
        self.assertEqual(result["mean_peak_allocated_mib"], 0)
        self.assertNotIn("accuracy", result)

    def test_session_three_frames_failure_partial_truncation_coverage(self):
        record = WebcamRecord(
            self.storage, "session-test", FakeCamera().identity(), SessionLimits(max_frames=3)
        )
        rows = []
        for i, status in enumerate(("complete", "partial", "failed")):
            data = fixture(f"frame-{i}", status)
            self.save(data)
            rows.append(analysis_row(data))
            record.captured(f"frame-{i}")
            record.submitted(f"frame-{i}")
        record.end("MAX_FRAME_LIMIT")
        record.cleanup({"mock_cleanup": True, "gpu_measured": False})
        row = session_row(record.data, rows)
        self.assertEqual(row["analysis_attempts"], 3)
        self.assertEqual(row["captured_frames"], 3)
        self.assertEqual(
            (row["completed_frames"], row["partial_frames"], row["failed_frames"]), (1, 1, 1)
        )
        self.assertEqual(row["total_model_calls"], 6)
        self.assertEqual(row["total_output_tokens"], 18)
        self.assertEqual(row["truncated_frame_count"], 3)
        self.assertEqual(row["mean_verification_coverage"], 0.5)
        self.assertEqual(row["median_analysis_latency_sec"], 2)
        self.assertIsNone(row["camera_release_success"])
        self.assertIsNone(row["model_cleanup_success"])
        out = export_bundle(self.storage)
        self.assertEqual(
            self.read_csv(out / "webcam_sessions.csv")[0]["camera_backend_type"], "FAKE"
        )

    def test_session_missing_result_not_complete_total(self):
        row = session_row(
            {"session_id": "session-test", "analysis_attempts": 3}, [analysis_row(fixture())]
        )
        self.assertIsNone(row["total_model_calls"])
        self.assertEqual(row["completed_frames"], 1)

    def test_cleanup_evidence_not_inferred_from_close_request(self):
        self.assertEqual(cleanup_status({"worker_exited": True}), "UNVERIFIED")
        self.assertEqual(cleanup_status({"mock_cleanup": True}), "MOCK_NOT_PHYSICAL_EVIDENCE")
        self.assertEqual(cleanup_status({"cleanup_error": "x"}), "FAIL")
        self.assertEqual(
            cleanup_status(
                {
                    "measurement": {"allocated_bytes": 0, "reserved_bytes": 0},
                    "worker_exited": True,
                    "job_empty": True,
                    "baseline_equivalent": True,
                }
            ),
            "PASS",
        )

    def test_receipts_filter_input_and_keep_failed_started_call(self):
        events = [
            {"phase": "call_start", "input_id": "other", "call_id": "call-1"},
            {
                "phase": "call_start",
                "input_id": "frame-1",
                "call_id": "call-1",
                "input_token_ids": [1, 2],
                "request": {"prompt_id": "test"},
            },
        ]
        (self.storage.root / "events.jsonl").write_text("\n".join(json.dumps(x) for x in events))
        receipts, error = read_frame_receipts(self.storage.root, "frame-1")
        self.assertIsNone(error)
        data = {
            "metadata": {"input_id": "frame-1", "source": "WEBCAM", "evidence_kind": REAL},
            "attempt_runtime": {"frame_trace": receipts, "calls_complete": True},
        }
        rows = call_rows(data)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["input_tokens"], 2)
        self.assertIsNone(rows[0]["raw_response"])
        self.assertIsNone(analysis_row(data)["output_tokens"])

    def test_unknown_evidence_not_relabelled_mock_or_real(self):
        data = fixture()
        del data["metadata"]["evidence_kind"]
        row = analysis_row(data)
        self.assertTrue(row["record_schema_version"].endswith("/UNKNOWN"))
        self.assertIsNone(row["peak_allocated_mib"])

    def test_unfinished_generation_truncation_unknown_not_zero(self):
        data = fixture(real=True)
        data["report"]["runtime_metadata"]["frame_trace"] = [
            {"call_id": "call-3", "input_tokens": 5, "call_started": True}
        ]
        self.assertIsNone(analysis_row(data)["truncated_call_count"])
        self.assertIsNone(analysis_row(data)["output_tokens"])

    def test_cleanup_sidecar_export_preserves_raw(self):
        ref = self.save(fixture(real=True))
        raw = self.storage.path(ref).read_bytes()
        self.storage.save(
            self.storage.path(ref).parent, {"cleanup_error": "failed"}, "session_cleanup.json"
        )
        row = self.read_csv(export_bundle(self.storage) / "analysis_summary.csv")[0]
        self.assertEqual(row["cleanup_status"], "FAIL")
        self.assertEqual(self.storage.path(ref).read_bytes(), raw)

    def test_corrupt_session_audited(self):
        (self.storage.allocate("bad-session") / "session.json").write_text("[]")
        out = export_bundle(self.storage)
        self.assertIn("CORRUPT_SESSION", (out / "export_audit.json").read_text())

    def test_manifest_matches_canonical_source(self):
        ref = self.save(fixture())
        out = export_bundle(self.storage)
        audit = json.loads((out / "export_audit.json").read_text())
        self.assertEqual(
            audit["source_sha256"][ref],
            hashlib.sha256(self.storage.path(ref).read_bytes()).hexdigest(),
        )


class NewQtFlowTests(unittest.TestCase):
    # Reuse setup/teardown only; do not duplicate the existing tests/count.
    setUp = QtFlowTests.setUp
    tearDown = QtFlowTests.tearDown

    def test_three_tabs_review_and_export_from_history(self):
        self.assertEqual(
            [self.window.tabs.tabText(i) for i in range(3)], ["分析", "詳細資料", "歷史紀錄"]
        )
        self.window.select_path(self.path)
        spin(lambda: self.window.selected is not None)
        self.window.analyze_manual()
        spin(lambda: not self.window.controller.busy)
        self.window._history_selected(0, 0)
        self.window.review_rating.setCurrentText("USABLE")
        self.window.review_note.setPlainText("繁中可用，保留限制")
        self.window._save_review()
        self.window._export("all")
        self.assertIn("已匯出", self.window.history_status.text())
        self.assertIn("Agent State Trace", self.window.details.toPlainText())
        self.assertEqual(self.storage.review(self.window.selected_record)["human_rating"], "USABLE")

    def test_fake_three_frames_one_session_aggregate_and_stop(self):
        self.window.session_limits = SessionLimits(max_frames=3)
        now = [0.0]
        self.window.controller.clock = lambda: now[0]
        self.window._open_camera()
        self.window._start_auto()
        for i in range(3):
            spin(
                lambda expected=i + 1: (
                    len(self.storage.history()) == expected and not self.window.controller.busy
                )
            )
            now[0] += 5
            self.window._tick()
        self.assertFalse(self.window.controller.auto)
        self.assertFalse(self.camera.opened)
        sessions = self.storage.sessions()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0][1]["analysis_attempts"], 3)
        self.assertEqual(sessions[0][1]["session_stop_reason"], "MAX_FRAME_LIMIT")
        self.window._export("all")
        self.assertEqual(len(list(self.storage.root.glob("export-*/webcam_sessions.csv"))), 1)
        self.assertFalse(list(self.storage.root.glob("*/frame.png")))

    def test_export_disabled_while_auto_or_busy(self):
        self.window._open_camera()
        self.window._start_auto()
        self.assertTrue(all(not button.isEnabled() for button in self.window.export_buttons))
        self.window._export("all")
        self.assertFalse(list(self.storage.root.glob("export-*")))
        self.window.stop_webcam()

    def test_qt_physical_backend_stub_capture_has_no_fake_dependency(self):
        camera = QtCamera(self.window.video_preview)
        device = MagicMock()
        device.id.return_value = QByteArray(b"physical-id")
        device.description.return_value = "Test USB"
        camera.session = MagicMock()
        camera.capture_device = MagicMock()
        camera.capture_device.isReadyForCapture.return_value = True
        camera.capture_device.capture.return_value = 4
        physical = MagicMock()
        with (
            patch("local_vision_agent.app_camera.QMediaDevices.videoInputs", return_value=[device]),
            patch("local_vision_agent.app_camera.QCamera", return_value=physical),
        ):
            self.assertEqual(camera.devices(), ["Test USB"])
            camera.open(0)
            self.assertEqual(camera.identity()["camera_backend_type"], "QT_MULTIMEDIA_PHYSICAL")
            self.assertEqual(camera.identity()["camera_id"], b"physical-id".hex())
            delivered = []
            camera.frame.connect(lambda i, image: delivered.append(i))
            camera.capture("frame-1")
            camera._captured(99, QImage())
            self.assertEqual(delivered, [])
            camera._captured(4, QImage(8, 8, QImage.Format.Format_RGB32))
            self.assertEqual(delivered, ["frame-1"])
            camera.close()
            camera._captured(4, QImage())
            self.assertEqual(delivered, ["frame-1"])
            physical.stop.assert_called_once()
            camera.open(0)
            camera.close()

    def test_qt_device_list_drift_refused_before_open(self):
        camera = QtCamera(self.window.video_preview)
        a = MagicMock()
        a.id.return_value = QByteArray(b"a")
        b = MagicMock()
        b.id.return_value = QByteArray(b"b")
        with patch("local_vision_agent.app_camera.QMediaDevices.videoInputs", return_value=[a]):
            camera.devices()
        with (
            patch("local_vision_agent.app_camera.QMediaDevices.videoInputs", return_value=[b]),
            self.assertRaisesRegex(RuntimeError, "DEVICE_LIST_CHANGED"),
        ):
            camera.open(0)
        self.assertIsNone(camera.camera)


# unittest discovery would otherwise collect the imported original TestCase too.
del QtFlowTests

if __name__ == "__main__":
    unittest.main()
