from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

from backend.app.schemas.action import ActionPlan, ApprovalRequest, NextBestAction
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
    now = datetime.now()

    return {
        "investigation_id": investigation_id,
        "case_id": None,
        "status": InvestigationStatus.PENDING,
        "current_stage": AgentStage.TRIGGER,
        "step": 0,
        "max_steps": max_steps,
        "trigger": trigger,
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
    now = datetime.now()

    updated = dict(state)
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
    updated = dict(state)
    updated["errors"] = [
        *state.get("errors", []),
        error,
    ]
    updated["updated_at"] = datetime.now()

    return updated


def is_step_limit_reached(
    state: AgentRuntimeState,
) -> bool:
    return state.get("step", 0) >= state.get("max_steps", 20)