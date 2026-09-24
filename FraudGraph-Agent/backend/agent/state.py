from __future__ import annotations

from typing import Any, TypeAlias, TypedDict

from backend.app.schemas.agent import AgentStage
from backend.app.schemas.investigation import InvestigationStatus


class AgentState(TypedDict, total=False):
    # ------------------------------------------------------------------
    # Investigation identity
    # ------------------------------------------------------------------
    investigation_id: str
    case_id: str

    # ------------------------------------------------------------------
    # Trigger
    # ------------------------------------------------------------------
    trigger: dict[str, Any]
    trigger_type: str
    trigger_text: str

    # ------------------------------------------------------------------
    # Primary entities
    # ------------------------------------------------------------------
    customer_id: str
    card_id: str
    transaction_id: str
    flagged_txn_id: str

    # ------------------------------------------------------------------
    # Transaction / model context
    # ------------------------------------------------------------------
    transaction: dict[str, Any]
    bank_risk_score: float | None

    ml_fraud_probability: float | None
    ml_prediction: bool | None
    ml_model_version: str | None
    ml_error: str | None

    # ------------------------------------------------------------------
    # Investigation evidence
    # ------------------------------------------------------------------
    evidence: list[dict[str, Any]]
    evidence_ids: list[str]

    graph_evidence: list[dict[str, Any]]
    historical_evidence: list[dict[str, Any]]

    related_cases: list[dict[str, Any]]
    similar_cases: list[dict[str, Any]]

    # ------------------------------------------------------------------
    # Fraud patterns
    # ------------------------------------------------------------------
    pattern_findings: list[dict[str, Any]]
    patterns: list[dict[str, Any]]
    fraud_findings: list[dict[str, Any]]

    fraud_type: str | None

    # ------------------------------------------------------------------
    # Risk assessment
    # ------------------------------------------------------------------
    investigation_risk_score: float | None
    risk_score: float | None
    risk_level: str | None
    risk_confidence: float | None
    risk_uncertainty: float | None

    risk_assessment: dict[str, Any]
    assessment: dict[str, Any]

    # ------------------------------------------------------------------
    # Evidence sufficiency / uncertainty
    # ------------------------------------------------------------------
    evidence_sufficient: bool
    requires_additional_evidence: bool
    uncertainty: float | None

    required_evidence: list[str]
    evidence_requests: list[dict[str, Any]]

    # ------------------------------------------------------------------
    # Findings
    # ------------------------------------------------------------------
    findings: list[dict[str, Any]]
    finding_ids: list[str]

    # ------------------------------------------------------------------
    # Next-best-action
    # ------------------------------------------------------------------
    action_candidates: list[dict[str, Any]]
    recommended_action: dict[str, Any]
    next_best_action: dict[str, Any]

    action_reason: str | None
    action_confidence: float | None

    # ------------------------------------------------------------------
    # Approval
    # ------------------------------------------------------------------
    approval_required: bool
    approval_status: str | None
    approval_route: str | None
    approval_request: dict[str, Any] | None

    # ------------------------------------------------------------------
    # Action execution
    # ------------------------------------------------------------------
    action_executed: bool
    action_execution: dict[str, Any] | None
    action_result: dict[str, Any] | None

    # ------------------------------------------------------------------
    # Explanation
    # ------------------------------------------------------------------
    explanation: dict[str, Any]
    explanation_summary: str | None

    # ------------------------------------------------------------------
    # Case / memory
    # ------------------------------------------------------------------
    case: dict[str, Any]
    case_status: str | None

    memory_candidates: list[dict[str, Any]]
    memory_updates: list[dict[str, Any]]

    # ------------------------------------------------------------------
    # SAR / reporting
    # ------------------------------------------------------------------
    sar: dict[str, Any] | None

    # ------------------------------------------------------------------
    # Workflow control
    # ------------------------------------------------------------------
    current_stage: str | None
    status: str | None
    progress: float

    stop_reason: str | None
    investigation_complete: bool

    # ------------------------------------------------------------------
    # Events / observability
    # ------------------------------------------------------------------
    events: list[dict[str, Any]]
    tool_calls: list[dict[str, Any]]

    # ------------------------------------------------------------------
    # Performance
    # ------------------------------------------------------------------
    started_at: str | None
    completed_at: str | None
    latency_s: float | None
    tokens: int | None

    # ------------------------------------------------------------------
    # Errors
    # ------------------------------------------------------------------
    error: str | None
    warnings: list[str]

    # Extras that some node classes track on the state dict directly
    max_steps: int
    step: int
    errors: list[str]
    metadata: dict[str, Any]
    updated_at: str | None


# ---------------------------------------------------------------------------
# AgentRuntimeState is the canonical alias used throughout the codebase.
# It is identical to AgentState; the alias avoids a global rename while
# keeping the TypedDict definition in one place.
# ---------------------------------------------------------------------------
AgentRuntimeState: TypeAlias = AgentState


def advance_state(
    state: AgentRuntimeState,
    stage: Any,
    message: str | None = None,
) -> AgentRuntimeState:
    """Return a shallow copy of *state* with stage/step advanced.

    Every node calls this to stamp the current workflow stage and
    increment the step counter before making its own updates.
    """
    updated = dict(state)
    updated["current_stage"] = stage
    updated["step"] = int(state.get("step") or 0) + 1  # type: ignore[arg-type]
    metadata = dict(state.get("metadata") or {})
    if message is not None:
        metadata["last_message"] = message
    updated["metadata"] = metadata
    return updated  # type: ignore[return-value]


def add_error(state: AgentRuntimeState, error: str) -> AgentRuntimeState:
    """Add an error message to the state errors list and update the error field."""
    updated = dict(state)
    errors = list(state.get("errors") or [])
    errors.append(error)
    updated["errors"] = errors
    updated["error"] = error
    return updated  # type: ignore[return-value]


def is_step_limit_reached(state: AgentRuntimeState) -> bool:
    """Return True if the current step count has reached or exceeded max_steps."""
    step = int(state.get("step") or 0)
    max_steps = int(state.get("max_steps") or 20)
    return step >= max_steps


def create_initial_state(
    investigation_id: str,
    trigger: dict[str, Any] | None = None,
    max_steps: int = 20,
) -> AgentState:
    """
    Create a clean state for a new investigation.

    The state is intentionally explicit so every major agent stage
    can enrich the same investigation context without relying on
    hidden/global variables.
    """

    trigger = trigger or {}

    trigger_type = str(
        trigger.get("trigger_type")
        or trigger.get("type")
        or "unknown"
    )

    transaction_id = (
        trigger.get("transaction_id")
        or trigger.get("flagged_txn_id")
    )

    state: AgentState = {
        "investigation_id": investigation_id,

        "trigger": trigger,
        "trigger_type": trigger_type,
        "trigger_text": str(
            trigger.get("trigger_text")
            or trigger.get("text")
            or ""
        ),

        "customer_id": str(trigger["customer_id"])
        if trigger.get("customer_id") is not None
        else "",

        "card_id": str(trigger["card_id"])
        if trigger.get("card_id") is not None
        else "",

        "transaction_id": str(transaction_id)
        if transaction_id is not None
        else "",

        "flagged_txn_id": str(transaction_id)
        if transaction_id is not None
        else "",

        "transaction": {},

        "bank_risk_score": None,

        "ml_fraud_probability": None,
        "ml_prediction": None,
        "ml_model_version": None,
        "ml_error": None,

        "evidence": [],
        "evidence_ids": [],

        "graph_evidence": [],
        "historical_evidence": [],

        "related_cases": [],
        "similar_cases": [],

        "pattern_findings": [],
        "patterns": [],
        "fraud_findings": [],

        "fraud_type": None,

        "investigation_risk_score": None,
        "risk_score": None,
        "risk_level": None,
        "risk_confidence": None,
        "risk_uncertainty": None,

        "risk_assessment": {},
        "assessment": {},

        "evidence_sufficient": False,
        "requires_additional_evidence": False,
        "uncertainty": None,

        "required_evidence": [],
        "evidence_requests": [],

        "findings": [],
        "finding_ids": [],

        "action_candidates": [],
        "recommended_action": {},
        "next_best_action": {},

        "action_reason": None,
        "action_confidence": None,

        "approval_required": False,
        "approval_status": None,
        "approval_route": None,
        "approval_request": None,

        "action_executed": False,
        "action_execution": None,
        "action_result": None,

        "explanation": {},
        "explanation_summary": None,

        "case": {},
        "case_status": None,

        "memory_candidates": [],
        "memory_updates": [],

        "sar": None,

        "current_stage": AgentStage.TRIGGER,
        "status": InvestigationStatus.PENDING,
        "progress": 0.0,

        "stop_reason": None,
        "investigation_complete": False,

        "events": [],
        "tool_calls": [],

        "started_at": None,
        "completed_at": None,
        "latency_s": None,
        "tokens": None,

        "error": None,
        "warnings": [],

        # Step tracking
        "max_steps": max_steps,
        "step": 0,
        "errors": [],
        "metadata": {},
        "updated_at": None,
    }

    # Preserve the original bank risk score when it is present
    # in the trigger.
    risk_score = trigger.get("risk_score")

    if risk_score is not None:
        try:
            state["bank_risk_score"] = max(
                0.0,
                min(1.0, float(risk_score)),
            )
        except (TypeError, ValueError):
            state["warnings"].append(
                "Invalid trigger risk_score was ignored."
            )

    return state