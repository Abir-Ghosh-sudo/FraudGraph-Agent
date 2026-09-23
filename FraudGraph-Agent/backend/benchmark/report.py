from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any


class BenchmarkReportGenerator:
    """Formats benchmark evaluation metrics into JSON and Markdown reports."""

    def generate_json_report(
        self,
        run_id: str,
        evaluation: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "run_id": run_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "evaluation": evaluation,
        }

    def generate_markdown_report(
        self,
        run_id: str,
        evaluation: dict[str, Any],
    ) -> str:
        metrics = evaluation.get("metrics", {})
        lines = [
            f"# Fraud Detection Benchmark Report: {run_id}",
            f"**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "## Summary",
            f"- **Total Cases:** {evaluation.get('total_cases', 0)}",
            f"- **Completed Cases:** {evaluation.get('completed_cases', 0)}",
            f"- **Failed Cases:** {evaluation.get('failed_cases', 0)}",
            "",
            "## Performance Metrics",
            f"- **Precision:** {metrics.get('precision', 0.0):.2%}",
            f"- **Recall:** {metrics.get('recall', 0.0):.2%}",
            f"- **F1 Score:** {metrics.get('f1', 0.0):.4f}",
            f"- **Accuracy:** {metrics.get('accuracy', 0.0):.2%}",
            f"- **Brier Score (Calibration):** {metrics.get('brier_score', 0.0):.4f}",
            f"- **Average Latency:** {metrics.get('average_latency_ms', 0.0):.1f} ms",
        ]
        return "\n".join(lines)
