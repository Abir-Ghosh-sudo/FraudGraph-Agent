
from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class ActionType(StrEnum):
    ALLOW_TRANSACTION = "allow_transaction"
    BLOCK_TRANSACTION = "block_transaction"
    MONITOR_TRANSACTION = "monitor_transaction"
    WARN_CUSTOMER = "warn_customer"
    BLOCK_ACCOUNT = "block_account"
    MONITOR_ACCOUNT = "monitor_account"
    REQUEST_CUSTOMER_VALIDATION = "request_customer_validation"
    REQUEST_STEP_UP_AUTHENTICATION = "request_step_up_authentication"
    REQUEST_ANALYST_REVIEW = "request_analyst_review"
    REQUEST_ADDITIONAL_EVIDENCE = "request_additional_evidence"
    CREATE_CASE = "create_case"
    FILE_REPORT = "file_report"
    CLOSE_CASE = "close_case"


class ActionStatus(StrEnum):
    PROPOSED = "proposed"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ApprovalStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRoute(StrEnum):
    NONE = "none"
    ANALYST = "analyst"
    SENIOR_ANALYST = "senior_analyst"
    COMPLIANCE = "compliance"
    ADMINISTRATOR = "administrator"


class ActionRiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: ActionType

    title: str = Field(
        min_length=1,
        max_length=300,
    )

    rationale: str = Field(
        min_length=1,
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    required_evidence: list[str] = Field(
        default_factory=list,
    )

    risk_level: ActionRiskLevel = ActionRiskLevel.MEDIUM

    requires_approval: bool = True

    approval_route: ApprovalRoute = ApprovalRoute.ANALYST

    policy_references: list[str] = Field(
        default_factory=list,
    )

    priority: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )


class NextBestAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str

    action_type: ActionType

    title: str = Field(
        min_length=1,
        max_length=300,
    )

    rationale: str = Field(
        min_length=1,
    )

    status: ActionStatus = ActionStatus.PROPOSED

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    policy_references: list[str] = Field(
        default_factory=list,
    )

    risk_level: ActionRiskLevel = ActionRiskLevel.MEDIUM

    priority: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    requires_approval: bool = True

    approval_status: ApprovalStatus = ApprovalStatus.PENDING

    approval_route: ApprovalRoute = ApprovalRoute.ANALYST

    case_id: str | None = None

    investigation_id: str | None = None

    created_at: datetime = Field(
        default_factory=utc_now,
    )


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approval_id: str

    action_id: str

    route: ApprovalRoute

    status: ApprovalStatus = ApprovalStatus.PENDING

    reason: str = Field(
        min_length=1,
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    requested_by: str = Field(
        min_length=1,
    )

    requested_at: datetime = Field(
        default_factory=utc_now,
    )

    reviewed_by: str | None = None

    reviewed_at: datetime | None = None

    reviewer_note: str | None = None


class ActionExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str

    approved_by: str | None = None

    approval_id: str | None = None

    parameters: dict[str, Any] = Field(
        default_factory=dict,
    )


class ActionExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str

    status: ActionStatus

    success: bool

    message: str

    external_reference: str | None = None

    result: dict[str, Any] = Field(
        default_factory=dict,
    )

    executed_at: datetime | None = Field(
        default_factory=utc_now,
    )


class ActionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidates: list[ActionCandidate] = Field(
        default_factory=list,
    )

    selected_action: NextBestAction | None = None

    explanation: str | None = None

    requires_human_approval: bool = True

