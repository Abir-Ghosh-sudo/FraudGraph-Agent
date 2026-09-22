from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.investigation import RiskLevel


class CaseStatus(StrEnum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    AWAITING_EVIDENCE = "awaiting_evidence"
    AWAITING_APPROVAL = "awaiting_approval"
    ACTIONED = "actioned"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CaseOutcome(StrEnum):
    CONFIRMED_FRAUD = "confirmed_fraud"
    CLEARED = "cleared"
    INCONCLUSIVE = "inconclusive"
    ESCALATED = "escalated"


class DecisionType(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"
    MONITOR = "monitor"
    WARN = "warn"
    REQUEST_EVIDENCE = "request_evidence"
    ESCALATE = "escalate"
    CREATE_REPORT = "create_report"
    CLOSE = "close"


class CaseFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_id: str

    title: str = Field(
        min_length=1,
    )

    description: str = Field(
        min_length=1,
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    created_at: datetime


class CaseDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_id: str

    decision_type: DecisionType

    rationale: str = Field(
        min_length=1,
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    requires_approval: bool = False

    approved: bool | None = None

    approved_by: str | None = None

    created_at: datetime


class CaseAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str

    action_type: str = Field(
        min_length=1,
    )

    status: str = Field(
        default="proposed",
        min_length=1,
    )

    rationale: str | None = None

    requires_approval: bool = False

    approval_id: str | None = None

    result: dict[str, Any] = Field(
        default_factory=dict,
    )

    created_at: datetime

    completed_at: datetime | None = None


class CaseMemoryReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_id: str

    case_id: str

    similarity: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    relevance_reason: str | None = None


class CaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    investigation_id: str

    transaction_id: str | None = None

    customer_id: str | None = None

    account_id: str | None = None

    title: str = Field(
        min_length=1,
        max_length=300,
    )

    description: str | None = None


class CaseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: CaseStatus | None = None

    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    risk_level: RiskLevel | None = None

    outcome: CaseOutcome | None = None

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=300,
    )

    description: str | None = None


class Case(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str

    investigation_id: str

    transaction_id: str | None = None

    customer_id: str | None = None

    account_id: str | None = None

    title: str

    description: str | None = None

    status: CaseStatus = CaseStatus.OPEN

    outcome: CaseOutcome | None = None

    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    risk_level: RiskLevel = RiskLevel.UNKNOWN

    fraud_type: str | None = None

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    findings: list[CaseFinding] = Field(
        default_factory=list,
    )

    decisions: list[CaseDecision] = Field(
        default_factory=list,
    )

    actions: list[CaseAction] = Field(
        default_factory=list,
    )

    related_cases: list[CaseMemoryReference] = Field(
        default_factory=list,
    )

    memory_ids: list[str] = Field(
        default_factory=list,
    )

    created_at: datetime

    updated_at: datetime

    resolved_at: datetime | None = None

    closed_at: datetime | None = None