from __future__ import annotations

from backend.agent.nodes.execute_action import ExecuteActionNode
from backend.app.config import Settings
from backend.app.schemas.action import (
    ActionStatus,
    ApprovalRequest,
    ApprovalRoute,
    ApprovalStatus,
    NextBestAction,
)
from backend.app.schemas.agent import AgentEventType


def make_action(*, approved: bool = False) -> NextBestAction:
    return NextBestAction(
        action_id="act-node-test",
        action_type="block_transaction",
        title="Block transaction",
        rationale="Unit test",
        requires_approval=True,
        approval_status=(ApprovalStatus.APPROVED if approved else ApprovalStatus.PENDING),
    )


def test_enabled_execution_without_handler_is_reported_as_failed() -> None:
    action = make_action(approved=True)
    approval = ApprovalRequest(
        approval_id="appr-node-test",
        action_id=action.action_id,
        route=ApprovalRoute.ANALYST,
        status=ApprovalStatus.APPROVED,
        reason="Approved for unit test",
        requested_by="requester",
    )
    state = {
        "investigation_id": "inv-node-test",
        "selected_action": action,
        "approval": approval,
        "events": [],
        "step": 0,
        "max_steps": 10,
    }

    result = ExecuteActionNode(Settings(allow_action_execution=True)).run(state)

    assert result["action_execution"]["status"] == ActionStatus.FAILED.value
    assert result["action_execution"]["success"] is False
    assert result["action_execution"]["external_reference"] is None
    assert result["events"][-1].event_type == AgentEventType.ACTION_FAILED
    assert not any(event.event_type == AgentEventType.ACTION_EXECUTED for event in result["events"])


def test_missing_approval_does_not_emit_execution_event() -> None:
    state = {
        "investigation_id": "inv-node-no-approval",
        "selected_action": make_action(),
        "events": [],
        "step": 0,
        "max_steps": 10,
    }

    result = ExecuteActionNode(Settings(allow_action_execution=True)).run(state)

    assert "action_execution" not in result
    assert not any(event.event_type == AgentEventType.ACTION_EXECUTED for event in result["events"])