from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.action import ActionPlan, NextBestAction
from backend.app.schemas.evidence import Evidence
from backend.app.schemas.investigation import (
    InvestigationAssessment,
    InvestigationStatus,
)


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class AgentStage(StrEnum):
    TRIGGER = "trigger"
    INVESTIGATE = "investigate"
    GATHER_EVIDENCE = "gather_evidence"
    DETECT_PATTERNS = "detect_patterns"
    ASSESS_RISK = "assess_risk"
    ASSESS_UNCERTAINTY = "assess_uncERTAINTY"
    REQUEST_EVIDENCE = "request_evidence"
    REASSESS = "reassess"
    RECOMMEND_ACTION = "recommend_action"
    APPROVAL = "approval"
    EXECUTE_ACTION = "execute_action"
    EXPLAIN = "explain"
    UPDATE_MEMORY = "update_memory"
    COMPLETE = "complete"


class AgentEventType(StrEnum):
    INVESTIGATION_STARTED = "investigation_started"
    STAGE_STARTED = "stage_started"
    EVIDENCE_FOUND = "evidence_found"
    PATTERN_DETECTED = "pattern_detected"
    RISK_ASSESSED = "risk_assessed"
    UNCERTAINTY_ASSESSED = "uncertainty_assessed"
    EVIDENCE_REQUESTED = "evidence_requested"
    ACTION_RECOMMENDED = "action_recommended"
    APPROVAL_REQUESTED = "approval_requested"
    ACTION_EXECUTED = "action_executed"
    CASE_UPDATED = "case_updated"
    MEMORY_UPDATED = "memory_updated"
    INVESTIGATION_COMPLETED = "investigation_completed"
    INVESTIGATION_FAILED = "investigation_failed"


class EvidenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str

    reason: str = Field(
        min_length=1,
    )

    requested_evidence: list[str] = Field(
        default_factory=list,
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    approval_required: bool = True

    approval_route: str | None = None

    created_at: datetime = Field(
        default_factory=utc_now,
    )


class AgentDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: str = Field(
        min_length=1,
    )

    rationale: str = Field(
        min_length=1,
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    created_at: datetime = Field(
        default_factory=utc_now,
    )


class AgentExplanation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(
        min_length=1,
    )

    evidence_used: list[str] = Field(
        default_factory=list,
    )

    reasoning_points: list[str] = Field(
        default_factory=list,
    )

    uncertainty: list[str] = Field(
        default_factory=list,
    )

    additional_evidence_reason: str | None = None

    action_reason: str | None = None


class AgentEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str

    event_type: AgentEventType

    investigation_id: str

    case_id: str | None = None

    stage: AgentStage

    message: str = Field(
        min_length=1,
    )

    payload: dict[str, Any] = Field(
        default_factory=dict,
    )

    created_at: datetime = Field(
        default_factory=utc_now,
    )


class AgentState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    investigation_id: str

    case_id: str | None = None

    status: InvestigationStatus = InvestigationStatus.PENDING

    current_stage: AgentStage = AgentStage.TRIGGER

    step: int = Field(
        default=0,
        ge=0,
    )

    max_steps: int = Field(
        default=20,
        ge=1,
    )

    evidence: list[Evidence] = Field(
        default_factory=list,
    )

    evidence_requests: list[EvidenceRequest] = Field(
        default_factory=list,
    )

    assessment: InvestigationAssessment = Field(
        default_factory=InvestigationAssessment,
    )

    decisions: list[AgentDecision] = Field(
        default_factory=list,
    )

    action_plan: ActionPlan | None = None

    selected_action: NextBestAction | None = None

    explanation: AgentExplanation | None = None

    events: list[AgentEvent] = Field(
        default_factory=list,
    )

    errors: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    started_at: datetime | None = None

    updated_at: datetime | None = None

    completed_at: datetime | None = None