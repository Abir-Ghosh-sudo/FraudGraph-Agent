from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEventType, AgentStage
from backend.app.schemas.investigation import InvestigationStatus

logger = get_logger(__name__)


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def _make_event(
    state: AgentRuntimeState,
    event_type: AgentEventType,
    message: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a normalized agent event."""
    return {
        "event_id": f"evt_{uuid4().hex[:12]}",
        "event_type": event_type,
        "investigation_id": state.get("investigation_id", ""),
        "case_id": state.get("case_id"),
        "stage": AgentStage.TRIGGER,
        "message": message,
        "payload": payload or {},
        "created_at": utc_now(),
    }


class TriggerNode:
    """
    Entry-point node for a fraud investigation.

    Responsibilities:
    - Validate the incoming investigation trigger.
    - Verify that a usable investigation target exists.
    - Record the investigation-start event.
    - Move the investigation into the investigating state.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def __call__(
        self,
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        """Execute trigger validation and initialize investigation state."""
        return self.run(state)

    def run(
        self,
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        """Execute the trigger node."""
        trigger = state.get("trigger", {})
        investigation_id = state.get("investigation_id", "")

        if not isinstance(trigger, dict):
            trigger = {}

        logger.info(
            "investigation triggered",
            investigation_id=investigation_id,
            trigger_type=trigger.get("trigger_type"),
            transaction_id=trigger.get("transaction_id"),
            customer_id=trigger.get("customer_id"),
            account_id=trigger.get("account_id"),
        )

        errors = list(state.get("errors", []))

        has_target = any(
            bool(trigger.get(field))
            for field in (
                "transaction_id",
                "customer_id",
                "account_id",
            )
        )

        trigger_type = trigger.get("trigger_type")

        if not trigger_type:
            errors.append(
                "Trigger must specify a trigger_type."
            )

        if not has_target:
            errors.append(
                "Trigger must specify at least one of: "
                "transaction_id, customer_id, account_id."
            )

        updated = advance_state(
            state,
            AgentStage.TRIGGER,
        )

        updated["errors"] = errors
        updated["updated_at"] = utc_now()

        events = list(state.get("events", []))

        if errors:
            logger.warning(
                "trigger validation failed",
                investigation_id=investigation_id,
                errors=errors,
            )

            events.append(
                _make_event(
                    updated,
                    AgentEventType.INVESTIGATION_FAILED,
                    (
                        f"Investigation {investigation_id} "
                        "failed trigger validation."
                    ),
                    payload={
                        "errors": errors,
                        "trigger_type": trigger_type,
                    },
                )
            )

            updated["events"] = events
            updated["status"] = InvestigationStatus.FAILED

            return updated

        events.append(
            _make_event(
                updated,
                AgentEventType.INVESTIGATION_STARTED,
                (
                    f"Investigation {investigation_id} triggered: "
                    f"{trigger_type}"
                ),
                payload={
                    "trigger_type": trigger_type,
                    "transaction_id": trigger.get(
                        "transaction_id"
                    ),
                    "customer_id": trigger.get(
                        "customer_id"
                    ),
                    "account_id": trigger.get(
                        "account_id"
                    ),
                    "reason": trigger.get("reason"),
                },
            )
        )

        updated["events"] = events
        updated["status"] = InvestigationStatus.INVESTIGATING

        metadata = dict(
            state.get("metadata", {})
        )

        metadata["trigger_validated"] = True
        metadata["trigger_type"] = trigger_type
        metadata["trigger_target"] = {
            key: trigger.get(key)
            for key in (
                "transaction_id",
                "customer_id",
                "account_id",
            )
            if trigger.get(key)
        }

        updated["metadata"] = metadata

        return updated


def trigger_node(
    state: AgentRuntimeState,
    settings: Settings,
) -> AgentRuntimeState:
    """Functional wrapper for the trigger node."""
    return TriggerNode(
        settings=settings,
    ).run(state)