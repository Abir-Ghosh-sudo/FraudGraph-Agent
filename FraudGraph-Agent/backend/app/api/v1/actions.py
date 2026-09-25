from __future__ import annotations

from datetime import UTC, datetime

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
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix="/actions",
    tags=["actions"],
)


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

    return plan


@router.get(
    "/{action_id}",
    response_model=NextBestAction,
)
async def get_action(
    action_id: str,
    service: InvestigationService = Depends(get_investigation_service),
) -> NextBestAction:
    for investigation in service.list():
        state = service.get_state(investigation.investigation_id)
        if state is None:
            continue

        action = state.get("selected_action")
        if action is not None and action.action_id == action_id:
            return action

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
    for investigation in service.list():
        state = service.get_state(investigation.investigation_id)
        if state is None:
            continue

        approval = state.get("approval")
        if approval is not None and approval.approval_id == approval_id:
            return approval

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
    """Fail closed until a real registered provider handler is configured.

    Client-supplied approver identities are deliberately not accepted. An
    approval ID is only accepted when the matching server-side investigation
    state contains an approved request bound to this exact action.
    """
    now = datetime.now(UTC)
    selected_action: NextBestAction | None = None
    matching_approval: ApprovalRequest | None = None

    for investigation in service.list():
        state = service.get_state(investigation.investigation_id)
        if state is None:
            continue

        action = state.get("selected_action")
        if action is None or action.action_id != payload.action_id:
            continue

        selected_action = action
        approval = state.get("approval")
        if (
            approval is not None
            and payload.approval_id is not None
            and approval.approval_id == payload.approval_id
        ):
            matching_approval = approval
        break

    if selected_action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action '{payload.action_id}' is not registered for an investigation.",
        )

    if selected_action.requires_approval:
        approved = (
            matching_approval is not None
            and matching_approval.status == ApprovalStatus.APPROVED
            and matching_approval.action_id == selected_action.action_id
            and selected_action.approval_status == ApprovalStatus.APPROVED
        )
        if not approved:
            return ActionExecutionResult(
                action_id=payload.action_id,
                status=ActionStatus.PENDING_APPROVAL,
                success=False,
                message=(
                    "No matching server-side approved request was found. No action was performed."
                ),
                executed_at=now,
            )

    if not settings.allow_action_execution:
        return ActionExecutionResult(
            action_id=payload.action_id,
            status=ActionStatus.CANCELLED,
            success=False,
            message="Action execution is disabled. No action was performed.",
            executed_at=now,
        )

    # There is currently no provider handler wired into this API. Returning
    # success here would create a false operational/audit record.
    return ActionExecutionResult(
        action_id=payload.action_id,
        status=ActionStatus.FAILED,
        success=False,
        message=("No real action handler is configured. The action was not performed."),
        executed_at=now,
    )


__all__ = [
    "execute_action",
    "get_action",
    "get_action_plan",
    "get_approval",
]