from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.action import ApprovalRequest, ApprovalRoute, ApprovalStatus
from backend.app.schemas.agent import AgentEvent, AgentEventType, AgentStage
from backend.app.schemas.investigation import InvestigationStatus

logger = get_logger("agent.nodes.approval")


class ApprovalNode:
    """Creates an ApprovalRequest when the selected action requires human authorization."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, state: AgentRuntimeState) -> AgentRuntimeState:
        updated = advance_state(state, AgentStage.APPROVAL)

        selected_action = updated.get("selected_action")
        if not selected_action:
            return updated

        requires_approval = (
            selected_action.get("requires_approval")
            if isinstance(selected_action, dict)
            else getattr(selected_action, "requires_approval", False)
        )
        if not requires_approval:
            return updated

        action_id = (
            selected_action.get("action_id")
            if isinstance(selected_action, dict)
            else getattr(selected_action, "action_id", "")
        )
        title = (
            selected_action.get("title")
            if isinstance(selected_action, dict)
            else getattr(selected_action, "title", "Recommended Action")
        )
        route = (
            selected_action.get("approval_route")
            if isinstance(selected_action, dict)
            else getattr(selected_action, "approval_route", ApprovalRoute.ANALYST)
        ) or ApprovalRoute.ANALYST
        evidence_ids = (
            selected_action.get("evidence_ids", [])
            if isinstance(selected_action, dict)
            else getattr(selected_action, "evidence_ids", [])
        )

        approval = ApprovalRequest(
            approval_id=f"appr_{uuid4().hex[:12]}",
            action_id=action_id,
            route=route,
            status=ApprovalStatus.PENDING,
            reason=f"Action '{title}' requires authorization per risk policy.",
            evidence_ids=evidence_ids,
            requested_by="FraudGraph-Agent",
            requested_at=datetime.now(UTC),
        )

        updated["approval"] = approval
        updated["status"] = InvestigationStatus.AWAITING_APPROVAL

        event = AgentEvent(
            event_id=str(uuid4()),
            event_type=AgentEventType.APPROVAL_REQUESTED,
            investigation_id=updated.get("investigation_id", ""),
            case_id=updated.get("case_id"),
            stage=AgentStage.APPROVAL,
            message=f"Approval requested for action '{selected_action.title}' route: {approval.route.value}",
            payload={
                "approval_id": approval.approval_id,
                "action_id": approval.action_id,
                "route": approval.route.value,
            },
            created_at=datetime.now(UTC),
        )
        updated["events"] = [*updated.get("events", []), event]

        return updated
