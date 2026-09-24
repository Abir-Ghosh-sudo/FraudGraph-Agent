from __future__ import annotations

import asyncio
import json
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from backend.app.config import Settings
from backend.app.dependencies import get_app_settings
from backend.benchmark.runner import BenchmarkRunner
from backend.ml.benchmark import FraudModelBenchmark
from backend.ml.inference import FraudModelInference
from backend.ml.transaction_loader import TransactionRecordLoader

router = APIRouter(
    prefix="/benchmark",
    tags=["benchmark"],
)


class BenchmarkStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BenchmarkRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_ids: list[str] = Field(default_factory=list)
    max_cases: int = Field(default=20, ge=1)


class BenchmarkRun(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: BenchmarkStatus
    total_cases: int = Field(default=0, ge=0)
    completed_cases: int = Field(default=0, ge=0)
    failed_cases: int = Field(default=0, ge=0)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class BenchmarkMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    value: float = Field(ge=0.0)
    description: str | None = None


class BenchmarkReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: BenchmarkStatus
    metrics: list[BenchmarkMetric] = Field(default_factory=list)
    case_count: int = Field(default=0, ge=0)
    output_reference: str | None = None


def _ml_benchmark_path(settings: Settings) -> Path:
    return settings.outputs_dir.parent / "artifacts" / "ml" / "fraud_benchmark.json"


def _run_ml_benchmark(settings: Settings) -> dict[str, Any]:
    inference = FraudModelInference(
        model_path=settings.fraud_model_path,
        metadata_path=settings.fraud_model_metadata_path,
        threshold=settings.fraud_model_threshold,
    )
    loader = TransactionRecordLoader(
        transactions_path=settings.raw_data_dir / "transactions.csv",
        identity_path=settings.raw_data_dir / "identity.csv",
        chunk_size=settings.dataset_chunk_size,
    )
    benchmark = FraudModelBenchmark(
        inference=inference,
        transaction_loader=loader,
    )
    cases = benchmark.load_cases(settings.raw_data_dir / "case_pack.csv")
    predictions = benchmark.evaluate(cases[: settings.benchmark_max_cases])
    output_path = _ml_benchmark_path(settings)
    benchmark.save_report(output_path, predictions)
    return json.loads(output_path.read_text(encoding="utf-8"))


_RUNNER_INSTANCE: BenchmarkRunner | None = None


def get_benchmark_runner(settings: Settings = Depends(get_app_settings)) -> BenchmarkRunner:
    global _RUNNER_INSTANCE
    if _RUNNER_INSTANCE is None:
        _RUNNER_INSTANCE = BenchmarkRunner(settings=settings)
    return _RUNNER_INSTANCE


@router.get(
    "",
    response_model=dict[str, Any],
)
async def get_benchmark(
    settings: Settings = Depends(get_app_settings),
) -> dict[str, Any]:
    output_path = _ml_benchmark_path(settings)
    if not output_path.exists():
        return {
            "benchmark_cases": 0,
            "ground_truth_available": False,
            "note": (
                "No ML benchmark report has been generated yet. "
                "POST /api/v1/benchmark to run it against the real case_pack.csv."
            ),
            "cases": [],
            "output_reference": str(output_path),
        }

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    payload["output_reference"] = str(output_path)
    return payload


@router.post(
    "",
    response_model=dict[str, Any],
)
async def run_benchmark(
    settings: Settings = Depends(get_app_settings),
) -> dict[str, Any]:
    try:
        payload = await asyncio.to_thread(_run_ml_benchmark, settings)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ML benchmark failed: {exc}",
        ) from exc

    payload["output_reference"] = str(_ml_benchmark_path(settings))
    return payload


@router.post(
    "/runs",
    response_model=BenchmarkRun,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_benchmark(
    payload: BenchmarkRunRequest,
    runner: BenchmarkRunner = Depends(get_benchmark_runner),
) -> BenchmarkRun:
    # Run benchmark in threadpool to avoid blocking event loop
    run_state = await asyncio.to_thread(
        runner.run,
        case_ids=payload.case_ids,
        max_cases=payload.max_cases,
    )
    return BenchmarkRun(
        run_id=run_state["run_id"],
        status=BenchmarkStatus(run_state["status"]),
        total_cases=run_state["total_cases"],
        completed_cases=run_state["completed_cases"],
        failed_cases=run_state["failed_cases"],
        started_at=run_state.get("started_at"),
        completed_at=run_state.get("completed_at"),
    )


@router.get(
    "/runs/{run_id}",
    response_model=BenchmarkRun,
)
async def get_benchmark_run(
    run_id: str,
    runner: BenchmarkRunner = Depends(get_benchmark_runner),
) -> BenchmarkRun:
    run_state = runner.get_run(run_id)
    if run_state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark run '{run_id}' not found.",
        )
    return BenchmarkRun(
        run_id=run_state["run_id"],
        status=BenchmarkStatus(run_state["status"]),
        total_cases=run_state["total_cases"],
        completed_cases=run_state["completed_cases"],
        failed_cases=run_state["failed_cases"],
        started_at=run_state.get("started_at"),
        completed_at=run_state.get("completed_at"),
    )


@router.get(
    "/runs/{run_id}/report",
    response_model=BenchmarkReport,
)
async def get_benchmark_report(
    run_id: str,
    runner: BenchmarkRunner = Depends(get_benchmark_runner),
) -> BenchmarkReport:
    report = runner.get_report(run_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report for benchmark run '{run_id}' not found.",
        )

    metric_items: list[BenchmarkMetric] = []
    raw_metrics = report.get("metrics", {})
    for k, v in raw_metrics.items():
        if isinstance(v, (int, float)):
            metric_items.append(
                BenchmarkMetric(
                    name=k,
                    value=float(v),
                    description=f"Evaluation metric: {k}",
                )
            )

    return BenchmarkReport(
        run_id=run_id,
        status=BenchmarkStatus.COMPLETED,
        metrics=metric_items,
        case_count=report.get("total_cases", 0),
        output_reference=f"data/benchmark/outputs/{run_id}.json",
    )
