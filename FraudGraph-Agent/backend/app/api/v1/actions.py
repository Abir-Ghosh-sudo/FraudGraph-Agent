from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.config import Settings
from backend.app.dependencies import (
    get_app_settings,
    get_investigation_service,
)
from backend.app.schemas.action import (
    ActionExecutionRequest,
    ActionExecutionResult,
    ActionPlan,
    ActionStatus,
    ApprovalRequest,
    ApprovalStatus,
    NextBestAction,
)
from backend.app.services.investigation import InvestigationService

router = APIRouter(
    prefix="/actions",
    tags=["actions"],
)

_ACTIONS_REGISTRY: dict[str, NextBestAction] = {}
_APPROVALS_REGISTRY: dict[str, ApprovalRequest] = {}


def register_action(action: NextBestAction) -> None:
    _ACTIONS_REGISTRY[action.action_id] = action


def register_approval(approval: ApprovalRequest) -> None:
    _APPROVALS_REGISTRY[approval.approval_id] = approval


@router.get(
    "/investigation/{investigation_id}",
    response_model=ActionPlan,
)
async def get_action_plan(
    investigation_id: str,
    service: InvestigationService = Depends(get_investigation_service),
) -> ActionPlan:
    state = service.get_state(investigation_id)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation '{investigation_id}' not found.",
        )

    plan = state.get("action_plan")
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No action plan generated for investigation '{investigation_id}'.",
        )

    if plan.selected_action:
        register_action(plan.selected_action)
    if state.get("approval"):
        register_approval(state["approval"])

    return plan


@router.get(
    "/{action_id}",
    response_model=NextBestAction,
)
async def get_action(
    action_id: str,
    service: InvestigationService = Depends(get_investigation_service),
) -> NextBestAction:
    if action_id in _ACTIONS_REGISTRY:
        return _ACTIONS_REGISTRY[action_id]

    # Search in active investigations
    for inv in service.list():
        state = service.get_state(inv.investigation_id)
        if state and state.get("selected_action"):
            act = state["selected_action"]
            if act.action_id == action_id:
                register_action(act)
                return act

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Action '{action_id}' not found.",
    )


@router.get(
    "/approvals/{approval_id}",
    response_model=ApprovalRequest,
)
async def get_approval(
    approval_id: str,
    service: InvestigationService = Depends(get_investigation_service),
) -> ApprovalRequest:
    if approval_id in _APPROVALS_REGISTRY:
        return _APPROVALS_REGISTRY[approval_id]

    for inv in service.list():
        state = service.get_state(inv.investigation_id)
        if state and state.get("approval"):
            appr = state["approval"]
            if appr.approval_id == approval_id:
                register_approval(appr)
                return appr

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Approval request '{approval_id}' not found.",
    )


@router.post(
    "/execute",
    response_model=ActionExecutionResult,
)
async def execute_action(
    payload: ActionExecutionRequest,
    settings: Settings = Depends(get_app_settings),
    service: InvestigationService = Depends(get_investigation_service),
) -> ActionExecutionResult:
    now = datetime.now(UTC)

    if not settings.allow_action_execution:
        return ActionExecutionResult(
            action_id=payload.action_id,
            status=ActionStatus.FAILED,
            success=False,
            message="Action execution is disabled in system settings (ALLOW_ACTION_EXECUTION=False).",
            executed_at=now,
        )

    # If action requires approval, verify approval status
    action = None
    if payload.action_id in _ACTIONS_REGISTRY:
        action = _ACTIONS_REGISTRY[payload.action_id]
    else:
        for inv in service.list():
            state = service.get_state(inv.investigation_id)
            if state and state.get("selected_action") and state["selected_action"].action_id == payload.action_id:
                action = state["selected_action"]
                break

    if action and action.requires_approval:
        if not payload.approved_by and not payload.approval_id:
            return ActionExecutionResult(
                action_id=payload.action_id,
                status=ActionStatus.PENDING_APPROVAL,
                success=False,
                message="Action requires human approval before execution.",
                executed_at=now,
            )

    return ActionExecutionResult(
        action_id=payload.action_id,
        status=ActionStatus.COMPLETED,
        success=True,
        message=f"Action '{payload.action_id}' executed successfully.",
        external_reference=f"ext_{uuid4().hex[:10]}",
        result=payload.parameters,
        executed_at=now,
    )