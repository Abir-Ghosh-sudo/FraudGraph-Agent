from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MetricScore:
    name: str
    value: float
    description: str | None = None


def compute_binary_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    """Compute precision, recall, f1, and accuracy from binary ground truth and predictions."""
    if not y_true or len(y_true) != len(y_pred):
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "accuracy": 0.0}

    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(y_true) if y_true else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
    }


def compute_calibration_score(y_true: list[int], probabilities: list[float]) -> float:
    """Mean squared error between binary labels and predicted probabilities (Brier score)."""
    if not y_true or len(y_true) != len(probabilities):
        return 0.0
    brier = sum((p - yt) ** 2 for yt, p in zip(y_true, probabilities)) / len(y_true)
    return round(brier, 4)
