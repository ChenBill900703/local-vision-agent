"""Explicit CPU fixtures; no natural-image replay or model execution."""

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from local_vision_agent.agent import Agent
from local_vision_agent.contracts import AgentError, Answer, Claim, ImageInput, Method, load_limits
from local_vision_agent.mock_adapter import MockAdapter
from local_vision_agent.reporting import to_json, to_markdown


class RecordingExecutor:
    def __init__(self, adapter):
        self.adapter = adapter
        self.requests = []

    def invoke(self, request, image, timeout_s):
        self.requests.append(request)
        return self.adapter.invoke(request, image)


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "mock.png"
        Image.new("RGB", (8, 8)).save(self.path)
        self.limits = replace(
            load_limits(Path(__file__).resolve().parents[1] / "configs/agent_mock.toml"),
            max_model_calls=8,
            max_tool_calls=8,
            max_iterations=8,
            max_memory_entries=8,
            max_output_tokens=128,
        )

    def run_case(self, count=8, cap=8, method=Method.D, failure=False):
        claims = tuple(f"CPU模擬候選{i}" for i in range(count))
        adapter = MockAdapter(
            {
                "caption": Answer(
                    "CPU模擬截斷",
                    claims[:4],
                    output_tokens=128,
                    generation_stop_reason="token_limit",
                    truncated=True,
                ),
                "scene": Answer("CPU模擬", claims[4:], output_tokens=4),
                "object": Answer("CPU模擬", output_tokens=1),
                "detail": Answer("CPU模擬", output_tokens=1),
                "verify": Answer("supported", verdict="supported", output_tokens=1),
            },
            failures=("verify",) if failure else (),
        )
        executor = RecordingExecutor(adapter)
        report = Agent(replace(self.limits, max_model_calls=cap), adapter, executor=executor).run(
            ImageInput("MOCK", self.path), method
        )
        return report, executor

    def test_eight_candidates_six_slots_fifo_and_report(self):
        r, e = self.run_case()
        self.assertEqual(len(e.requests), 8)
        self.assertEqual([q.claim for q in e.requests[2:]], [c.text for c in r.claims[:6]])
        self.assertEqual(
            (
                r.candidate_claim_count,
                r.verification_budget,
                r.verification_attempted,
                r.verification_completed,
                r.verification_unresolved_by_budget,
                r.verification_coverage_ratio,
            ),
            (8, 6, 6, 6, 2, 0.75),
        )
        self.assertEqual(r.status, "complete")
        self.assertEqual(r.completion, "COMPLETED_WITH_PARTIAL_VERIFICATION")
        self.assertEqual(r.stop_reason, "VERIFICATION_BUDGET_EXHAUSTED")
        self.assertEqual(r.investigation_stop, "NO_TRIGGER")
        self.assertEqual(r.states[-2:], ("REPORT", "STOP"))
        for c in r.claims[6:]:
            self.assertEqual(
                (c.status, c.verification_id, c.verification_reason),
                ("unresolved", None, "verification_budget_not_available"),
            )
        self.assertEqual(json.loads(to_json(r))["verification_completed"], 6)
        self.assertIn("75%", to_markdown(r))
        self.assertIn("truncated=true", to_markdown(r))
        self.assertEqual(r.observations[0].answer.output_tokens, 128)

    def test_under_exact_and_zero_candidate_boundaries(self):
        for count in (0, 3, 6):
            r, e = self.run_case(count)
            self.assertEqual(len(e.requests), 2 + count)
            self.assertEqual(r.verification_completed, count)
            self.assertEqual(r.verification_unresolved_by_budget, 0)
            self.assertEqual(r.verification_coverage_ratio, 1.0 if count else None)
            self.assertEqual(r.stop_reason, "COMPLETED")

    def test_zero_slots(self):
        r, e = self.run_case(cap=2)
        self.assertEqual(len(e.requests), 2)
        self.assertEqual(
            (r.verification_budget, r.verification_attempted, r.verification_completed), (0, 0, 0)
        )
        self.assertEqual(r.verification_unresolved_by_budget, 8)
        self.assertTrue(
            all(c.status == "unresolved" and c.verification_id is None for c in r.claims)
        )

    def test_buggy_planner_cannot_bypass_hard_limit(self):
        with patch("local_vision_agent.agent.verification_slots", return_value=999):
            r, e = self.run_case()
        self.assertEqual(r.stop_reason, "TOOL_CALL_LIMIT")
        self.assertEqual(r.status, "partial")
        self.assertEqual(len(e.requests), 8)

    def test_error_not_masked_as_bounded_completion(self):
        r, _e = self.run_case(failure=True)
        self.assertEqual(r.stop_reason, "TOOL_FAILURE")
        self.assertEqual(r.completion, "INCOMPLETE")
        self.assertEqual((r.verification_attempted, r.verification_completed), (1, 0))
        self.assertEqual(r.verification_stop, "INTERRUPTED")

    def test_a_b_no_verification_c_d_share_scheduler(self):
        for method, calls, completed in (
            (Method.A, 1, 0),
            (Method.B, 2, 0),
            (Method.C, 8, 4),
            (Method.D, 8, 6),
        ):
            r, e = self.run_case(method=method)
            self.assertEqual(len(e.requests), calls)
            self.assertEqual(r.verification_completed, completed)

    def test_claim_requires_verification_evidence(self):
        for status in ("supported", "contradicted"):
            with self.assertRaisesRegex(AgentError, "VERIFICATION_EVIDENCE_REQUIRED"):
                Claim("mock", ("call-1",), status=status)


if __name__ == "__main__":
    unittest.main()
