"""CPU fixtures only; synthetic pixels have no relationship to mock claims."""

import json
import multiprocessing
import subprocess
import sys
import tempfile
import time
import tomllib
import unittest
from dataclasses import fields, replace
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from local_vision_agent.agent import Agent
from local_vision_agent.contracts import (
    AgentError,
    Answer,
    ImageInput,
    Limits,
    Method,
    load_limits,
)
from local_vision_agent.mock_adapter import MockAdapter
from local_vision_agent.reporting import to_json, to_markdown

ROOT = Path(__file__).resolve().parents[1]


class InlineFixture:
    """Test-only executor for fast deterministic controller assertions."""

    def __init__(self, adapter):
        self.adapter = adapter

    def invoke(self, request, image, timeout_s):
        return self.adapter.invoke(request, image)


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "synthetic.png"
        Image.new("RGB", (8, 8), "white").save(self.path)
        self.item = ImageInput("synthetic-1", self.path)
        self.limits = load_limits(ROOT / "configs/agent_mock.toml")

    def run_agent(self, method=Method.D, adapter=None, **limits):
        adapter = adapter or MockAdapter()
        return Agent(replace(self.limits, **limits), adapter, executor=InlineFixture(adapter)).run(
            self.item, method
        )

    def test_a_single_pass_and_no_hidden_report_call(self):
        report = self.run_agent(Method.A)
        self.assertEqual(len(report.observations), 1)
        self.assertEqual(report.stop_reason, "COMPLETED")
        self.assertTrue(all(c.status == "model-proposed" for c in report.claims))

    def test_b_d_investigation_identical_only_verification_differs(self):
        b, d = self.run_agent(Method.B), self.run_agent(Method.D)
        self.assertEqual(
            b.observations, tuple(o for o in d.observations if o.request.prompt_id != "verify")
        )
        self.assertEqual(b.investigation_stop, "NO_NEW_EVIDENCE")
        self.assertTrue(all(c.verification_id for c in d.claims))

    def test_adaptive_branch_and_fixed_c(self):
        adapter = MockAdapter({"caption": Answer("模擬明確", ("模擬物件",), output_tokens=8)})
        d, c = self.run_agent(adapter=adapter), self.run_agent(Method.C, adapter)
        self.assertEqual(
            [o.request.prompt_id for o in d.observations], ["caption", "scene", "verify", "verify"]
        )
        self.assertEqual(
            [o.request.prompt_id for o in c.observations][:4],
            ["caption", "scene", "object", "detail"],
        )
        self.assertEqual(d.investigation_stop, "NO_TRIGGER")

    def test_detail_trigger_without_object_trigger(self):
        adapter = MockAdapter({"caption": Answer("模擬", missing=("detail",), output_tokens=2)})
        report = self.run_agent(Method.B, adapter)
        self.assertEqual(
            [o.request.prompt_id for o in report.observations], ["caption", "scene", "detail"]
        )

    def test_same_model_supported_contradicted_unresolved_are_preserved(self):
        for verdict in ("supported", "contradicted", "unresolved"):
            adapter = MockAdapter({"verify": Answer("模擬驗證", verdict=verdict, output_tokens=4)})
            report = self.run_agent(adapter=adapter)
            self.assertTrue(all(c.status == verdict for c in report.claims))
            self.assertIn("不是獨立真值", to_markdown(report))

    def test_all_safety_fields_required(self):
        with (ROOT / "configs/agent_mock.toml").open("rb") as handle:
            values = tomllib.load(handle)["limits"]
        for field in fields(Limits):
            missing = dict(values)
            del missing[field.name]
            with self.subTest(field=field.name), self.assertRaises(TypeError):
                Limits(**missing)
            for invalid in (0, -1, True, float("nan"), float("inf"), "5"):
                with self.subTest(field=field.name, invalid=invalid), self.assertRaises(AgentError):
                    Limits(**{**values, field.name: invalid})

    def test_rejects_legacy_and_unknown_configuration(self):
        with self.assertRaises(AgentError):
            load_limits(ROOT / "configs/models.toml")
        bad = Path(self.temp.name) / "bad.toml"
        bad.write_text('schema="agent-mock-v1"\nadapter="moondream2"\n', encoding="utf8")
        with self.assertRaises(AgentError):
            load_limits(bad)
        with self.assertRaises(AgentError):
            Agent(None, MockAdapter())
        with self.assertRaises(AgentError):
            Agent(self.limits, object())

    def test_call_model_iteration_memory_limits(self):
        for field, reason in (
            ("max_tool_calls", "TOOL_CALL_LIMIT"),
            ("max_model_calls", "MODEL_CALL_LIMIT"),
            ("max_iterations", "ITERATION_LIMIT"),
            ("max_memory_entries", "MEMORY_LIMIT"),
        ):
            report = self.run_agent(**{field: 1})
            self.assertEqual(report.stop_reason, reason)
            self.assertEqual(len(report.observations), 1)
            self.assertEqual(report.status, "partial")

    def test_tool_failure_preserves_memory_and_attempt(self):
        report = self.run_agent(adapter=MockAdapter(failures=("scene",)))
        self.assertEqual(report.stop_reason, "TOOL_FAILURE")
        self.assertEqual(len(report.observations), 2)
        self.assertEqual(len(report.claims), 1)
        self.assertEqual(report.observations[-1].error, "TOOL_FAILURE")

    def test_unsupported_core_tool_fails_without_fallback(self):
        report = self.run_agent(adapter=MockAdapter(capabilities=("caption",)))
        self.assertEqual(report.stop_reason, "UNSUPPORTED_TOOL")
        self.assertEqual(len(report.observations), 2)

    def test_malformed_empty_and_oversized_responses(self):
        for answer in (
            Answer("", output_tokens=1),
            Answer("x", verdict="truth", output_tokens=1),
            Answer("x", missing=("execute_python",), output_tokens=1),
            Answer("x", output_tokens=0),
        ):
            self.assertEqual(
                self.run_agent(adapter=MockAdapter({"caption": answer})).stop_reason,
                "INVALID_TOOL_RESULT",
            )
        self.assertEqual(self.run_agent(max_output_tokens=1).stop_reason, "OUTPUT_LIMIT")
        self.assertEqual(self.run_agent(max_response_chars=1).stop_reason, "OUTPUT_LIMIT")
        self.assertEqual(self.run_agent(max_input_tokens=1).stop_reason, "INPUT_TOKEN_LIMIT")
        report = self.run_agent(max_total_output_tokens=16)
        self.assertEqual(report.stop_reason, "OUTPUT_LIMIT")
        self.assertEqual(len(report.observations), 1)

    def test_bad_images_and_size_limits(self):
        for field, reason in (
            ("max_input_bytes", "IMAGE_BYTES_LIMIT"),
            ("max_pixels", "IMAGE_PIXELS_LIMIT"),
            ("max_image_edge_px", "IMAGE_EDGE_LIMIT"),
        ):
            report = self.run_agent(**{field: 1})
            self.assertEqual(report.stop_reason, reason)
            self.assertFalse(report.observations)
        self.path.write_bytes(b"not an image")
        self.assertEqual(self.run_agent().stop_reason, "INVALID_IMAGE")
        self.path.unlink()
        self.assertEqual(self.run_agent().stop_reason, "IMAGE_IO_ERROR")

    def test_jpeg_and_reject_other_formats(self):
        Image.new("RGB", (8, 8)).save(self.path, format="JPEG")
        self.assertEqual(self.run_agent(Method.A).image.format, "JPEG")
        Image.new("RGB", (8, 8)).save(self.path, format="GIF")
        self.assertEqual(self.run_agent().stop_reason, "UNSUPPORTED_IMAGE")

    def test_memory_dedup_and_per_image_reset(self):
        adapter = MockAdapter({"scene": Answer("模擬", ("桌上有杯子",), output_tokens=2)})
        agent = Agent(self.limits, adapter, executor=InlineFixture(adapter))
        reports = agent.run_batch([self.item, ImageInput("synthetic-2", self.path)], Method.D)
        self.assertEqual(len(reports[0].claims), 1)
        self.assertEqual(reports[0].claims[0].observation_ids, ("call-1", "call-2"))
        self.assertEqual(reports[0].claims, reports[1].claims)
        self.assertNotEqual(reports[0].run_id, reports[1].run_id)

    def test_batch_invalid_input_continues_and_tool_failure_halts(self):
        adapter = MockAdapter()
        agent = Agent(self.limits, adapter, executor=InlineFixture(adapter))
        reports = agent.run_batch([ImageInput("bad", self.path / "missing"), self.item], Method.A)
        self.assertEqual([r.status for r in reports], ["failed", "complete"])
        adapter = MockAdapter(failures=("caption",))
        reports = Agent(self.limits, adapter, executor=InlineFixture(adapter)).run_batch(
            [self.item, ImageInput("two", self.path)], Method.D
        )
        self.assertEqual(reports[1].stop_reason, "BATCH_HALTED")
        for items in ([], [self.item, self.item], [self.item] * 17):
            with self.assertRaises(AgentError):
                agent.run_batch(items, Method.A)

    def test_image_timeout_and_late_executor_result(self):
        adapter = MockAdapter()
        clock_values = iter([0, 61])
        report = Agent(
            self.limits, adapter, executor=InlineFixture(adapter), clock=lambda: next(clock_values)
        ).run(self.item, Method.D)
        self.assertEqual(report.stop_reason, "IMAGE_TIMEOUT")
        clock_values = iter([0, 0, 0, 6, 6])
        report = Agent(
            self.limits, adapter, executor=InlineFixture(adapter), clock=lambda: next(clock_values)
        ).run(self.item, Method.D)
        self.assertEqual(report.stop_reason, "TOOL_TIMEOUT")
        self.assertFalse(report.claims)

    def test_process_timeout_reaps_worker(self):
        before = {p.pid for p in multiprocessing.active_children()}
        adapter = MockAdapter(delays_s={"caption": 30})
        started = time.monotonic()
        report = Agent(replace(self.limits, per_call_timeout_s=0.3), adapter).run(
            self.item, Method.A
        )
        self.assertEqual(report.stop_reason, "TOOL_TIMEOUT")
        self.assertLess(time.monotonic() - started, 5)
        self.assertEqual(before, {p.pid for p in multiprocessing.active_children()})

    def test_real_spawn_success_and_error(self):
        report = Agent(self.limits, MockAdapter()).run(self.item, Method.D)
        self.assertEqual(report.status, "complete")
        report = Agent(self.limits, MockAdapter(failures=("caption",))).run(self.item, Method.A)
        self.assertEqual(report.stop_reason, "TOOL_FAILURE")

    def test_cleanup_failure_stops_batch(self):
        adapter = MockAdapter()
        executor = InlineFixture(adapter)
        with patch.object(executor, "invoke", side_effect=AgentError("CLEANUP_FAILED")):
            reports = Agent(self.limits, adapter, executor=executor).run_batch(
                [self.item, ImageInput("two", self.path)], Method.D
            )
        self.assertEqual(reports[0].stop_reason, "CLEANUP_FAILED")
        self.assertEqual(reports[1].status, "not_attempted")

    def test_report_json_links_and_inert_text(self):
        adapter = MockAdapter({"caption": Answer("<script>bad</script>", output_tokens=4)})
        report = self.run_agent(adapter=adapter)
        payload = json.loads(to_json(report))
        self.assertEqual(payload["evidence_kind"], "MOCK_NOT_RESEARCH_EVIDENCE")
        self.assertIsNone(payload["peak_vram_mib"])
        self.assertIn("&lt;script&gt;", to_markdown(report))
        self.assertNotIn("<script>", to_markdown(report))
        call_ids = {o.call_id for o in report.observations}
        for claim in report.claims:
            self.assertTrue(set(claim.observation_ids) <= call_ids)
            self.assertIn(claim.verification_id, call_ids)

    def test_cli_and_imports_do_not_load_model_frameworks(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "local_vision_agent.mock_cli",
                "--adapter",
                "mock",
                "--config",
                str(ROOT / "configs/agent_mock.toml"),
                "--image",
                str(self.path),
                "--input-id",
                "synthetic",
                "--method",
                "A",
            ],
            check=True,
            capture_output=True,
            encoding="utf8",
            timeout=15,
        )
        self.assertEqual(json.loads(result.stdout)["method"], "A")
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                (
                    "import local_vision_agent.agent, sys; "
                    "assert not {'torch','transformers','torchvision',"
                    "'local_vision_agent.routing','local_vision_agent.evaluation'} & set(sys.modules)"
                ),
            ],
            capture_output=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_legacy_models_disabled(self):
        with (ROOT / "configs/models.toml").open("rb") as handle:
            config = tomllib.load(handle)
        self.assertTrue(all(not model["enabled"] for model in config["models"].values()))

    def test_partial_verification_never_promotes_unchecked_claims(self):
        report = self.run_agent(max_tool_calls=5)
        self.assertEqual(report.stop_reason, "TOOL_CALL_LIMIT")
        self.assertEqual(report.claims[0].status, "unresolved")
        self.assertIsNotNone(report.claims[0].verification_id)
        self.assertEqual(report.claims[1].status, "model-proposed")
        self.assertIsNone(report.claims[1].verification_id)

    def test_config_missing_limit_and_typo_fail_closed(self):
        source = (ROOT / "configs/agent_mock.toml").read_text(encoding="utf8")
        path = Path(self.temp.name) / "missing.toml"
        for text in (
            source.replace("max_tool_calls = 12\n", ""),
            source.replace("max_tool_calls", "max_toll_calls"),
        ):
            path.write_text(text, encoding="utf8")
            with self.assertRaises(AgentError):
                load_limits(path)

    def test_new_detail_evidence_and_finite_queries(self):
        adapter = MockAdapter(
            {"detail": Answer("模擬紅色", ("杯子為紅色",), True, ("detail",), output_tokens=5)}
        )
        report = self.run_agent(Method.D, adapter)
        self.assertEqual(report.investigation_stop, "QUERY_SET_DONE")
        self.assertEqual(sum(o.request.prompt_id == "detail" for o in report.observations), 1)
        self.assertEqual(len(report.claims), 3)


if __name__ == "__main__":
    unittest.main()
