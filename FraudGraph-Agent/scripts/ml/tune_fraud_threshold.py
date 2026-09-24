from __future__ import annotations

import argparse
import json
from pathlib import Path


def calculate_metrics(
    cases: list[dict],
    threshold: float,
) -> dict[str, float | int]:
    tp = tn = fp = fn = 0

    for case in cases:
        actual = bool(case["actual_fraud"])
        predicted = float(case["probability"]) >= threshold

        if actual and predicted:
            tp += 1
        elif not actual and not predicted:
            tn += 1
        elif not actual and predicted:
            fp += 1
        else:
            fn += 1

    total = len(cases)

    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "threshold": threshold,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tune fraud decision threshold."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=Path(
            "artifacts/ml/fraud_benchmark.json"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "artifacts/ml/fraud_thresholds.json"
        ),
    )

    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Benchmark report not found: {args.input}"
        )

    payload = json.loads(
        args.input.read_text(encoding="utf-8")
    )

    cases = payload.get("cases", [])

    if not cases:
        raise ValueError("Benchmark report contains no cases.")

    thresholds = [
        round(0.30 + i * 0.05, 2)
        for i in range(13)
    ]

    results = [
        calculate_metrics(cases, threshold)
        for threshold in thresholds
    ]

    # For fraud investigation, retain the threshold with
    # the strongest F1 while preserving recall as the
    # primary tie-breaker.
    selected = max(
        results,
        key=lambda item: (
            float(item["f1"]),
            float(item["recall"]),
        ),
    )

    output = {
        "thresholds": results,
        "selected_threshold": selected,
        "selection_method": (
            "maximum_f1_then_recall"
        ),
    }

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )

    print("\n=== Fraud Threshold Analysis ===")

    for result in results:
        print(
            f"threshold={result['threshold']:.2f} "
            f"precision={result['precision']:.4f} "
            f"recall={result['recall']:.4f} "
            f"f1={result['f1']:.4f}"
        )

    print(
        f"\nSelected threshold: "
        f"{selected['threshold']:.2f}"
    )
    print(f"Report: {args.output}")


if __name__ == "__main__":
    main()