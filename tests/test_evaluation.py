import unittest

from local_vision_agent.evaluation import evaluate


def row(sample, target, prediction, split="test"):
    return dict(sample_id=sample, target=target, prediction=prediction, split=split)


class EvaluationTests(unittest.TestCase):
    def test_abstention_does_not_inflate_overall_accuracy(self):
        result = evaluate([row("1", "cat", "cat"), row("2", "dog", "")])
        self.assertEqual(result["coverage"], 0.5)
        self.assertEqual(result["accuracy_all_samples"], 0.5)
        self.assertEqual(result["selective_accuracy"], 1.0)
        self.assertEqual(result["macro_f1_all_samples"], 0.5)

    def test_all_abstentions_have_undefined_selective_metrics(self):
        result = evaluate([row("1", "cat", "")])
        self.assertIsNone(result["selective_accuracy"])
        self.assertIsNone(result["selective_risk"])
        self.assertEqual(result["macro_f1_all_samples"], 0.0)

    def test_wrong_answer_counts_in_risk(self):
        result = evaluate([row("1", "cat", "dog"), row("2", "dog", "dog")])
        self.assertEqual(result["selective_risk"], 0.5)
        self.assertAlmostEqual(result["macro_f1_all_samples"], 1 / 3)

    def test_rejects_empty_duplicate_non_test_and_unknown_labels(self):
        bad_tables = [[], [row("1", "cat", "cat")] * 2,
                      [row("1", "cat", "cat", "train")],
                      [row("1", "cat", "dog")], [{}]]
        for table in bad_tables:
            with self.subTest(table=table), self.assertRaises(ValueError):
                evaluate(table)
