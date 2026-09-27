"""Offline prediction-quality evaluation. Does not measure GPU cost or latency."""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable, Mapping
from pathlib import Path


def evaluate(rows: Iterable[Mapping[str, str]]) -> dict[str, object]:
    """Evaluate one complete held-out test split. Empty prediction means abstain.

    Overall accuracy treats abstention as not correct. Macro-F1 includes all
    classes observed in ground truth; predictions outside that vocabulary fail.
    Selective accuracy and risk are null when no samples are answered.
    This function cannot establish split provenance: callers must audit manifests.
    """
    records = list(rows)
    if not records:
        raise ValueError("Prediction table must not be empty")
    required = {"sample_id", "split", "target", "prediction"}
    seen: set[str] = set()
    for row in records:
        if not required.issubset(row):
            raise ValueError("Required columns: sample_id, split, target, prediction")
        if any(not isinstance(row[key], str) for key in required):
            raise ValueError("Prediction rows must contain string values")
        if not row["sample_id"].strip() or not row["target"].strip():
            raise ValueError("Sample ID and target must be nonempty")
        if row["sample_id"] in seen:
            raise ValueError("Duplicate sample ID")
        seen.add(row["sample_id"])
        if row["split"] != "test":
            raise ValueError("Only held-out test rows may enter final evaluation")
    labels = sorted({row["target"] for row in records})
    if any(row["prediction"] and row["prediction"] not in labels for row in records):
        raise ValueError("Prediction contains a label outside the test vocabulary")
    answered = sum(bool(row["prediction"]) for row in records)
    correct = sum(row["target"] == row["prediction"] for row in records)
    per_class: dict[str, dict[str, int | float]] = {}
    for label in labels:
        tp = sum(row["target"] == label and row["prediction"] == label for row in records)
        fp = sum(row["target"] != label and row["prediction"] == label for row in records)
        fn = sum(row["target"] == label and row["prediction"] != label for row in records)
        denominator = 2 * tp + fp + fn
        per_class[label] = {
            "support": tp + fn,
            "f1": 2 * tp / denominator if denominator else 0.0,
        }
    return {
        "schema_version": 1,
        "evaluation_kind": "offline_prediction_quality",
        "samples": len(records),
        "answered": answered,
        "abstained": len(records) - answered,
        "coverage": answered / len(records),
        "accuracy_all_samples": correct / len(records),
        "selective_accuracy": correct / answered if answered else None,
        "selective_risk": (answered - correct) / answered if answered else None,
        "macro_f1_all_samples": sum(item["f1"] for item in per_class.values()) / len(labels),
        "per_class": per_class,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        with args.input.open(encoding="utf-8-sig", newline="") as handle:
            result = evaluate(csv.DictReader(handle))
        # Refuse overwrite so earlier experiment evidence is preserved.
        payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(payload)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Evaluation failed: {error}\n")


if __name__ == "__main__":
    main()
