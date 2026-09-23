from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEventType, AgentStage
from backend.app.schemas.investigation import InvestigationStatus
from backend.agent.state import AgentRuntimeState, advance_state

logger = get_logger(__name__)


def _make_event(
    state: AgentRuntimeState,
    event_type: AgentEventType,
    message: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "event_id": f"evt_{uuid4().hex[:8]}",
        "event_type": event_type,
        "investigation_id": state.get("investigation_id", ""),
        "case_id": state.get("case_id"),
        "stage": AgentStage.TRIGGER,
        "message": message,
        "payload": payload or {},
        "created_at": datetime.now(UTC),
    }


class TriggerNode:
    """
    Entry point node.

    Validates the trigger payload, extracts the primary investigation target,
    updates investigation status to INVESTIGATING, and emits INVESTIGATION_STARTED.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def __call__(self, state: AgentRuntimeState) -> AgentRuntimeState:
        trigger = state.get("trigger", {})
        investigation_id = state.get("investigation_id", "")

        logger.info(
            "investigation triggered",
            investigation_id=investigation_id,
            trigger_type=trigger.get("trigger_type"),
            transaction_id=trigger.get("transaction_id"),
            customer_id=trigger.get("customer_id"),
        )

        errors = list(state.get("errors", []))

        # Validate that at least one target is specified
        has_target = any(
            trigger.get(k)
            for k in ("transaction_id", "customer_id", "account_id")
        )

        if not has_target:
            error_msg = (
                "Trigger must specify at least one of: "
                "transaction_id, customer_id, account_id."
            )
            errors.append(error_msg)
            logger.warning("trigger validation failed", error=error_msg)

        events = list(state.get("events", []))
        events.append(
            _make_event(
                state,
                AgentEventType.INVESTIGATION_STARTED,
                f"Investigation {investigation_id} triggered: "
                f"{trigger.get('trigger_type', 'unknown')}",
                payload={
                    "trigger_type": trigger.get("trigger_type"),
                    "transaction_id": trigger.get("transaction_id"),
                    "customer_id": trigger.get("customer_id"),
                    "account_id": trigger.get("account_id"),
                    "reason": trigger.get("reason"),
                },
            )
        )

        updated = advance_state(state, AgentStage.TRIGGER)
        updated["status"] = InvestigationStatus.INVESTIGATING
        updated["events"] = events
        updated["errors"] = errors

        return updated
