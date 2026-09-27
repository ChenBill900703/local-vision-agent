from __future__ import annotations

import unittest

from local_vision_agent.routing import ConfidenceRouter, ToolResult


class ConfidenceRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = ConfidenceRouter(
            accept_threshold=0.75,
            verification_threshold=0.65,
            conflict_margin=0.20,
        )

    def test_accepts_confident_primary_without_verifier(self) -> None:
        primary = ToolResult(model="clip", label="cat", confidence=0.91)
        decision = self.router.resolve(primary)
        self.assertEqual(decision.label, "cat")
        self.assertFalse(decision.abstained)
        self.assertEqual(decision.used_models, ("clip",))

    def test_abstains_when_low_primary_has_no_verifier(self) -> None:
        primary = ToolResult(model="clip", label="cat", confidence=0.50)
        decision = self.router.resolve(primary)
        self.assertTrue(decision.abstained)
        self.assertIsNone(decision.label)

    def test_accepts_agreement_above_verification_threshold(self) -> None:
        primary = ToolResult(model="clip", label="cat", confidence=0.60)
        verifier = ToolResult(model="dinov2", label="cat", confidence=0.80)
        decision = self.router.resolve(primary, verifier)
        self.assertEqual(decision.label, "cat")
        self.assertAlmostEqual(decision.confidence, 0.70)

    def test_accepts_clear_verifier_winner(self) -> None:
        primary = ToolResult(model="clip", label="cat", confidence=0.40)
        verifier = ToolResult(model="dinov2", label="dog", confidence=0.85)
        decision = self.router.resolve(primary, verifier)
        self.assertEqual(decision.label, "dog")
        self.assertFalse(decision.abstained)

    def test_abstains_on_close_disagreement(self) -> None:
        primary = ToolResult(model="clip", label="cat", confidence=0.60)
        verifier = ToolResult(model="dinov2", label="dog", confidence=0.70)
        decision = self.router.resolve(primary, verifier)
        self.assertTrue(decision.abstained)
        self.assertIsNone(decision.label)

    def test_rejects_invalid_confidence(self) -> None:
        with self.assertRaises(ValueError):
            ToolResult(model="clip", label="cat", confidence=1.1)


if __name__ == "__main__":
    unittest.main()

