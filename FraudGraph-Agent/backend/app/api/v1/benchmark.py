from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field


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

    case_ids: list[str] = Field(
        default_factory=list,
    )

    max_cases: int = Field(
        default=20,
        ge=1,
    )


class BenchmarkRun(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str

    status: BenchmarkStatus

    total_cases: int = Field(
        default=0,
        ge=0,
    )

    completed_cases: int = Field(
        default=0,
        ge=0,
    )

    failed_cases: int = Field(
        default=0,
        ge=0,
    )

    started_at: datetime | None = None

    completed_at: datetime | None = None


class BenchmarkMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str

    value: float = Field(
        ge=0.0,
    )

    description: str | None = None


class BenchmarkReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str

    status: BenchmarkStatus

    metrics: list[BenchmarkMetric] = Field(
        default_factory=list,
    )

    case_count: int = Field(
        default=0,
        ge=0,
    )

    output_reference: str | None = None


@router.post(
    "/runs",
    response_model=BenchmarkRun,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_benchmark(
    payload: BenchmarkRunRequest,
) -> BenchmarkRun:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Benchmark runner is not configured yet.",
    )


@router.get(
    "/runs/{run_id}",
    response_model=BenchmarkRun,
)
async def get_benchmark_run(
    run_id: str,
) -> BenchmarkRun:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Benchmark runner is not configured yet.",
    )


@router.get(
    "/runs/{run_id}/report",
    response_model=BenchmarkReport,
)
async def get_benchmark_report(
    run_id: str,
) -> BenchmarkReport:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Benchmark evaluator is not configured yet.",
    )