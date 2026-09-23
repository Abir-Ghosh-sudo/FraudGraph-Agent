from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from backend.agent.agent import FraudInvestigationAgent
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.investigation import RiskLevel
from backend.benchmark.evaluator import BenchmarkEvaluator
from backend.benchmark.report import BenchmarkReportGenerator

logger = get_logger("benchmark.runner")


class BenchmarkRunner:
    """Discovers, executes, evaluates, and stores fraud detection benchmark test cases."""

    def __init__(
        self,
        settings: Settings,
        agent: FraudInvestigationAgent | None = None,
    ) -> None:
        self.settings = settings
        self.agent = agent or FraudInvestigationAgent(settings=settings)
        self.evaluator = BenchmarkEvaluator()
        self.report_gen = BenchmarkReportGenerator()
        self._runs: dict[str, dict[str, Any]] = {}
        self._reports: dict[str, dict[str, Any]] = {}

    def discover_cases(self) -> list[Path]:
        cases_dir = self.settings.benchmark_cases_dir
        if not cases_dir.exists():
            return []
        return sorted(cases_dir.glob("*.json"))

    def run(
        self,
        case_ids: list[str] | None = None,
        max_cases: int | None = None,
    ) -> dict[str, Any]:
        run_id = f"run_{uuid4().hex[:12]}"
        now = datetime.now(UTC)
        max_c = max_cases or self.settings.benchmark_max_cases

        all_case_files = self.discover_cases()
        if case_ids:
            case_files = [f for f in all_case_files if f.stem in case_ids]
        else:
            case_files = all_case_files[:max_c]

        run_state: dict[str, Any] = {
            "run_id": run_id,
            "status": "running",
            "total_cases": len(case_files),
            "completed_cases": 0,
            "failed_cases": 0,
            "started_at": now,
            "completed_at": None,
        }
        self._runs[run_id] = run_state

        if not case_files:
            logger.info("no_benchmark_cases_found", directory=str(self.settings.benchmark_cases_dir))
            run_state["status"] = "completed"
            run_state["completed_at"] = datetime.now(UTC)
            eval_result = self.evaluator.evaluate([])
            self._reports[run_id] = eval_result
            return run_state

        case_results: list[dict[str, Any]] = []

        for case_file in case_files:
            case_id = case_file.stem
            t0 = time.perf_counter()
            try:
                content = json.loads(case_file.read_text(encoding="utf-8"))
                trigger = content.get("trigger", {})
                ground_truth = bool(content.get("is_fraud", False))

                state = self.agent.start(
                    investigation_id=f"bench_{case_id}_{run_id[:8]}",
                    trigger=trigger,
                )
                latency_ms = (time.perf_counter() - t0) * 1000.0

                assessment = state.get("assessment")
                risk_score = getattr(assessment, "risk_score", 0.0) or 0.0
                risk_level = getattr(assessment, "risk_level", RiskLevel.UNKNOWN)
                is_predicted_fraud = (
                    risk_score >= self.settings.risk_medium_threshold
                    or risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
                )

                case_results.append(
                    {
                        "case_id": case_id,
                        "ground_truth_fraud": ground_truth,
                        "predicted_fraud": is_predicted_fraud,
                        "predicted_risk_score": risk_score,
                        "latency_ms": latency_ms,
                        "error": None,
                    }
                )
                run_state["completed_cases"] += 1
            except Exception as exc:
                latency_ms = (time.perf_counter() - t0) * 1000.0
                logger.error("benchmark_case_execution_failed", case_id=case_id, error=str(exc))
                case_results.append(
                    {
                        "case_id": case_id,
                        "ground_truth_fraud": False,
                        "predicted_fraud": False,
                        "predicted_risk_score": 0.0,
                        "latency_ms": latency_ms,
                        "error": str(exc),
                    }
                )
                run_state["failed_cases"] += 1

        eval_result = self.evaluator.evaluate(case_results)
        self._reports[run_id] = eval_result

        run_state["status"] = "completed"
        run_state["completed_at"] = datetime.now(UTC)

        # Save report output to benchmark_outputs_dir
        try:
            self.settings.benchmark_outputs_dir.mkdir(parents=True, exist_ok=True)
            out_file = self.settings.benchmark_outputs_dir / f"{run_id}.json"
            json_report = self.report_gen.generate_json_report(run_id, eval_result)
            out_file.write_text(json.dumps(json_report, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning("failed_saving_benchmark_report_file", error=str(exc))

        return run_state

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        return self._runs.get(run_id)

    def get_report(self, run_id: str) -> dict[str, Any] | None:
        return self._reports.get(run_id)
