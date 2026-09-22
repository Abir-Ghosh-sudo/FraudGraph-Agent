from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.action import (
    ActionExecutionRequest,
    ActionExecutionResult,
    ActionPlan,
    ApprovalRequest,
    NextBestAction,
)


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
) -> ActionPlan:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Action planning service is not configured yet.",
    )


@router.get(
    "/{action_id}",
    response_model=NextBestAction,
)
async def get_action(
    action_id: str,
) -> NextBestAction:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Action service is not configured yet.",
    )


@router.get(
    "/approvals/{approval_id}",
    response_model=ApprovalRequest,
)
async def get_approval(
    approval_id: str,
) -> ApprovalRequest:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Approval service is not configured yet.",
    )


@router.post(
    "/execute",
    response_model=ActionExecutionResult,
)
async def execute_action(
    payload: ActionExecutionRequest,
) -> ActionExecutionResult:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Action execution service is not configured yet.",
    )