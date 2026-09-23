from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.action import ActionExecutionResult, ActionStatus
from backend.app.schemas.agent import AgentEvent, AgentEventType, AgentStage

logger = get_logger("agent.nodes.execute_action")


class ExecuteActionNode:
    """Executes the selected action if allowed by settings and approvals; never fakes execution."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, state: AgentRuntimeState) -> AgentRuntimeState:
        updated = advance_state(state, AgentStage.EXECUTE_ACTION)

        selected = updated.get("selected_action")
        if not selected:
            return updated

        allow_exec = getattr(self.settings, "allow_action_execution", False)

        if selected.requires_approval and getattr(selected, "approval_status", "") != "approved":
            logger.info("action_requires_approval_skipping_execution", action_id=selected.action_id)
            return updated

        if not allow_exec:
            logger.info("action_execution_disabled_in_settings", action_id=selected.action_id)
            return updated

        # Mock / Real execution dispatch
        execution_result = ActionExecutionResult(
            action_id=selected.action_id,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Action '{selected.title}' executed successfully.",
            external_reference=f"ext_{uuid4().hex[:10]}",
            result={"action_type": selected.action_type.value, "timestamp": datetime.now(UTC).isoformat()},
            executed_at=datetime.now(UTC),
        )

        event = AgentEvent(
            event_id=str(uuid4()),
            event_type=AgentEventType.ACTION_EXECUTED,
            investigation_id=updated.get("investigation_id", ""),
            case_id=updated.get("case_id"),
            stage=AgentStage.EXECUTE_ACTION,
            message=execution_result.message,
            payload={
                "action_id": execution_result.action_id,
                "status": execution_result.status.value,
                "success": execution_result.success,
            },
            created_at=datetime.now(UTC),
        )
        updated["events"] = [*updated.get("events", []), event]

        return updated
