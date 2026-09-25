from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from backend.app.api.v1.actions import execute_action
from backend.app.config import Settings
from backend.app.schemas.action import (
    ActionExecutionRequest,
    ActionStatus,
    ApprovalRequest,
    ApprovalRoute,
    ApprovalStatus,
    NextBestAction,
)
from fastapi import HTTPException


class FakeInvestigationService:
    def __init__(self, action: NextBestAction | None = None, approval=None) -> None:
        self.investigation = SimpleNamespace(investigation_id="inv-test")
        self.state = {"selected_action": action, "approval": approval}

    def list(self):
        return [self.investigation]

    def get_state(self, investigation_id: str):
        if investigation_id != self.investigation.investigation_id:
            return None
        return self.state


def make_action(*, requires_approval: bool = True, approved=False) -> NextBestAction:
    return NextBestAction(
        action_id="act-test",
        action_type="block_transaction",
        title="Block transaction",
        rationale="Test action",
        requires_approval=requires_approval,
        approval_status=(ApprovalStatus.APPROVED if approved else ApprovalStatus.PENDING),
    )


def make_approval(status: ApprovalStatus) -> ApprovalRequest:
    return ApprovalRequest(
        approval_id="appr-test",
        action_id="act-test",
        route=ApprovalRoute.ANALYST,
        status=status,
        reason="Test approval",
        requested_by="unit-test",
    )


def test_unknown_action_is_not_reported_as_success() -> None:
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            execute_action(
                ActionExecutionRequest(action_id="attacker-chosen-id"),
                Settings(allow_action_execution=True),
                FakeInvestigationService(),
            )
        )

    assert exc_info.value.status_code == 404


def test_unapproved_action_stays_pending_even_if_client_supplies_approval_id() -> None:
    result = asyncio.run(
        execute_action(
            ActionExecutionRequest(action_id="act-test", approval_id="fake-id"),
            Settings(allow_action_execution=True),
            FakeInvestigationService(make_action(), make_approval(ApprovalStatus.PENDING)),
        )
    )

    assert result.status == ActionStatus.PENDING_APPROVAL
    assert result.success is False
    assert result.external_reference is None


def test_approved_action_without_provider_handler_does_not_claim_success() -> None:
    result = asyncio.run(
        execute_action(
            ActionExecutionRequest(action_id="act-test", approval_id="appr-test"),
            Settings(allow_action_execution=True),
            FakeInvestigationService(
                make_action(approved=True),
                make_approval(ApprovalStatus.APPROVED),
            ),
        )
    )

    assert result.status == ActionStatus.FAILED
    assert result.success is False
    assert result.external_reference is None
    assert "not performed" in result.message


def test_execution_disabled_never_returns_completed() -> None:
    result = asyncio.run(
        execute_action(
            ActionExecutionRequest(action_id="act-test"),
            Settings(allow_action_execution=False),
            FakeInvestigationService(make_action(requires_approval=False)),
        )
    )

    assert result.status == ActionStatus.CANCELLED
    assert result.success is False
    assert result.external_reference is None