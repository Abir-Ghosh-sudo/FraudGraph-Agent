from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field


router = APIRouter(
    prefix="/policies",
    tags=["policies"],
)


class PolicyEvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: str = Field(
        min_length=1,
    )

    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
    )

    context: dict[str, Any] = Field(
        default_factory=dict,
    )


class PolicyEvaluationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool

    requires_approval: bool

    approval_route: str | None = None

    policy_references: list[str] = Field(
        default_factory=list,
    )

    restrictions: list[str] = Field(
        default_factory=list,
    )

    rationale: str = Field(
        min_length=1,
    )


@router.post(
    "/evaluate",
    response_model=PolicyEvaluationResult,
)
async def evaluate_policy(
    payload: PolicyEvaluationRequest,
) -> PolicyEvaluationResult:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Policy engine is not configured yet.",
    )


@router.get(
    "/{policy_id}",
)
async def get_policy(
    policy_id: str,
) -> dict[str, Any]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Policy service is not configured yet.",
    )