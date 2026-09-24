from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class InvestigationTriggerType(StrEnum):
    FRAUD_SIGNAL = "fraud_signal"
    CUSTOMER_REPORT = "customer_report"
    ANALYST_REQUEST = "analyst_request"


class InvestigationStatus(StrEnum):
    PENDING = "pending"
    INVESTIGATING = "investigating"
    AWAITING_EVIDENCE = "awaiting_evidence"
    AWAITING_APPROVAL = "awaiting_approval"
    ACTION_RECOMMENDED = "action_recommended"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    FAILED = "failed"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class InvestigationTrigger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trigger_type: InvestigationTriggerType

    transaction_id: str | None = Field(
        default=None,
        min_length=1,
    )

    customer_id: str | None = Field(
        default=None,
        min_length=1,
    )

    account_id: str | None = Field(
        default=None,
        min_length=1,
    )

    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    reason: str | None = Field(
        default=None,
        min_length=1,
    )

    requested_by: str | None = Field(
        default=None,
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class InvestigationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trigger: InvestigationTrigger

    priority: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    requested_at: datetime = Field(
        default_factory=utc_now,
    )


class InvestigationProgress(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int = Field(
        default=0,
        ge=0,
    )

    max_steps: int = Field(
        default=20,
        ge=1,
    )

    current_stage: str | None = None

    message: str | None = None

    completed_stages: list[str] = Field(
        default_factory=list,
    )


class InvestigationAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    risk_level: RiskLevel = RiskLevel.UNKNOWN

    uncertainty: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    fraud_type: str | None = None

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    rationale: str | None = None

    bank_risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    ml_fraud_probability: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    ml_used: bool = False

    ml_model_version: str | None = None

    graph_evidence_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    pattern_evidence_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    historical_case_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    trigger_type: str | None = None


class InvestigationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    findings: list[str] = Field(
        default_factory=list,
    )

    recommendations: list[str] = Field(
        default_factory=list,
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    related_case_ids: list[str] = Field(
        default_factory=list,
    )

    requires_additional_evidence: bool = False

    required_evidence: list[str] = Field(
        default_factory=list,
    )


class Investigation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    investigation_id: str

    status: InvestigationStatus = InvestigationStatus.PENDING

    trigger: InvestigationTrigger

    progress: InvestigationProgress = Field(
        default_factory=InvestigationProgress,
    )

    assessment: InvestigationAssessment = Field(
        default_factory=InvestigationAssessment,
    )

    result: InvestigationResult = Field(
        default_factory=InvestigationResult,
    )

    case_id: str | None = None

    created_at: datetime = Field(
        default_factory=utc_now,
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
    )

    completed_at: datetime | None = None