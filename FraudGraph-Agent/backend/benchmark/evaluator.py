from __future__ import annotations

from typing import Any

from backend.benchmark.metrics import compute_binary_metrics, compute_calibration_score


class BenchmarkEvaluator:
    """Evaluates fraud detection benchmark results against ground truth labels."""

    def evaluate(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """
        results item format:
        {
            "case_id": str,
            "ground_truth_fraud": bool,
            "predicted_fraud": bool,
            "predicted_risk_score": float,
            "latency_ms": float,
            "error": str | None
        }
        """
        if not results:
            return {
                "total_cases": 0,
                "completed_cases": 0,
                "failed_cases": 0,
                "metrics": {},
            }

        valid_results = [r for r in results if not r.get("error")]
        failed_count = len(results) - len(valid_results)

        y_true = [1 if r.get("ground_truth_fraud") else 0 for r in valid_results]
        y_pred = [1 if r.get("predicted_fraud") else 0 for r in valid_results]
        probabilities = [float(r.get("predicted_risk_score", 0.0)) for r in valid_results]

        metrics = compute_binary_metrics(y_true, y_pred)
        metrics["brier_score"] = compute_calibration_score(y_true, probabilities)

        latencies = [float(r.get("latency_ms", 0.0)) for r in valid_results]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        metrics["average_latency_ms"] = round(avg_latency, 2)

        return {
            "total_cases": len(results),
            "completed_cases": len(valid_results),
            "failed_cases": failed_count,
            "metrics": metrics,
        }
