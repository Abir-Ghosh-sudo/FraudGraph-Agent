from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypedDict

from backend.app.schemas.action import (
    ActionPlan,
    ApprovalRequest,
    NextBestAction,
)
from backend.app.schemas.agent import (
    AgentDecision,
    AgentEvent,
    AgentExplanation,
    AgentStage,
    EvidenceRequest,
)
from backend.app.schemas.evidence import Evidence
from backend.app.schemas.graph import InvestigationSubgraph
from backend.app.schemas.investigation import (
    InvestigationAssessment,
    InvestigationStatus,
)


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class AgentRuntimeState(TypedDict, total=False):
    investigation_id: str
    case_id: str | None

    status: InvestigationStatus
    current_stage: AgentStage

    step: int
    max_steps: int

    trigger: dict[str, Any]

    graph: InvestigationSubgraph | None

    evidence: list[Evidence]
    evidence_requests: list[EvidenceRequest]

    detected_patterns: list[dict[str, Any]]
    related_cases: list[dict[str, Any]]

    assessment: InvestigationAssessment

    decisions: list[AgentDecision]

    action_plan: ActionPlan | None
    selected_action: NextBestAction | None
    approval: ApprovalRequest | None

    explanation: AgentExplanation | None

    events: list[AgentEvent]
    errors: list[str]

    started_at: datetime | None
    updated_at: datetime | None
    completed_at: datetime | None

    metadata: dict[str, Any]


def create_initial_state(
    investigation_id: str,
    trigger: dict[str, Any],
    max_steps: int,
) -> AgentRuntimeState:
    """Create the initial runtime state for an investigation."""
    now = utc_now()

    return {
        "investigation_id": investigation_id,
        "case_id": None,
        "status": InvestigationStatus.PENDING,
        "current_stage": AgentStage.TRIGGER,
        "step": 0,
        "max_steps": max(1, max_steps),
        "trigger": dict(trigger),
        "graph": None,
        "evidence": [],
        "evidence_requests": [],
        "detected_patterns": [],
        "related_cases": [],
        "assessment": InvestigationAssessment(),
        "decisions": [],
        "action_plan": None,
        "selected_action": None,
        "approval": None,
        "explanation": None,
        "events": [],
        "errors": [],
        "started_at": now,
        "updated_at": now,
        "completed_at": None,
        "metadata": {},
    }


def advance_state(
    state: AgentRuntimeState,
    stage: AgentStage,
    *,
    message: str | None = None,
) -> AgentRuntimeState:
    """Advance the investigation to the next agent stage."""
    now = utc_now()

    updated: AgentRuntimeState = dict(state)

    updated["current_stage"] = stage
    updated["step"] = state.get("step", 0) + 1
    updated["updated_at"] = now

    if message:
        metadata = dict(state.get("metadata", {}))
        metadata["last_message"] = message
        updated["metadata"] = metadata

    return updated


def add_error(
    state: AgentRuntimeState,
    error: str,
) -> AgentRuntimeState:
    """Add an error without mutating the existing state."""
    updated: AgentRuntimeState = dict(state)

    errors = list(state.get("errors", []))
    errors.append(error)

    updated["errors"] = errors
    updated["updated_at"] = utc_now()

    return updated


def is_step_limit_reached(
    state: AgentRuntimeState,
) -> bool:
    """Return whether the investigation reached its configured step limit."""
    return state.get("step", 0) >= state.get("max_steps", 20)