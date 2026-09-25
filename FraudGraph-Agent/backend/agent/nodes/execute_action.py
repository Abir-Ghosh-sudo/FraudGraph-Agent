from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.action import ActionExecutionResult, ActionStatus, ApprovalStatus
from backend.app.schemas.agent import AgentEvent, AgentEventType, AgentStage

logger = get_logger("agent.nodes.execute_action")


class ExecuteActionNode:
    """Fail safely when execution is disabled or no real handler is wired."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, state: AgentRuntimeState) -> AgentRuntimeState:
        updated = advance_state(state, AgentStage.EXECUTE_ACTION)
        selected = updated.get("selected_action")
        if selected is None:
            return updated

        approval = updated.get("approval")
        if selected.requires_approval:
            approval_is_valid = (
                approval is not None
                and approval.status == ApprovalStatus.APPROVED
                and approval.action_id == selected.action_id
                and selected.approval_status == ApprovalStatus.APPROVED
            )
            if not approval_is_valid:
                logger.warning(
                    "action_execution_blocked_without_matching_approval",
                    action_id=selected.action_id,
                )
                return updated

        if not self.settings.allow_action_execution:
            logger.info(
                "action_execution_disabled_in_settings",
                action_id=selected.action_id,
            )
            updated["action_execution"] = ActionExecutionResult(
                action_id=selected.action_id,
                status=ActionStatus.CANCELLED,
                success=False,
                message="Action execution is disabled. No action was performed.",
                executed_at=datetime.now(UTC),
            ).model_dump(mode="json")
            return updated

        # No provider handler is currently injected into this node. It must
        # report failure rather than claiming that an external action ran.
        now = datetime.now(UTC)
        result = ActionExecutionResult(
            action_id=selected.action_id,
            status=ActionStatus.FAILED,
            success=False,
            message=("No real action handler is configured. The action was not performed."),
            executed_at=now,
        )
        updated["action_execution"] = result.model_dump(mode="json")

        event = AgentEvent(
            event_id=str(uuid4()),
            event_type=AgentEventType.ACTION_FAILED,
            investigation_id=updated.get("investigation_id", ""),
            case_id=updated.get("case_id"),
            stage=AgentStage.EXECUTE_ACTION,
            message=result.message,
            payload={
                "action_id": result.action_id,
                "status": result.status.value,
                "success": False,
                "performed": False,
            },
            created_at=now,
        )
        updated["events"] = [*updated.get("events", []), event]
        logger.error("action_handler_not_configured", action_id=selected.action_id)
        return updated