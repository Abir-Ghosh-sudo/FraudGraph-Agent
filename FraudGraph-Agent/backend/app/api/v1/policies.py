from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from backend.app.dependencies import get_policy_engine
from backend.policy.engine import PolicyEngine

router = APIRouter(
    prefix="/policies",
    tags=["policies"],
)


class PolicyEvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: str = Field(min_length=1)
    risk_score: float | None = Field(default=None, ge=0.0, le=1.0)
    risk_level: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)


class PolicyEvaluationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool
    requires_approval: bool
    approval_route: str | None = None
    policy_references: list[str] = Field(default_factory=list)
    restrictions: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)
    source: str = "default_rules"


@router.post(
    "/evaluate",
    response_model=PolicyEvaluationResponse,
)
async def evaluate_policy(
    payload: PolicyEvaluationRequest,
    engine: PolicyEngine = Depends(get_policy_engine),
) -> PolicyEvaluationResponse:
    res = engine.evaluate_action(
        payload.action_type,
        risk_score=payload.risk_score,
        risk_level=payload.risk_level,
        evidence_ids=payload.evidence_ids,
        context=payload.context,
    )
    return PolicyEvaluationResponse(
        allowed=res.allowed,
        requires_approval=res.requires_approval,
        approval_route=res.approval_route.value if hasattr(res.approval_route, "value") else str(res.approval_route),
        policy_references=res.policy_references,
        restrictions=res.restrictions,
        rationale=res.rationale,
        source=res.source,
    )


@router.get(
    "/{policy_id}",
)
async def get_policy(
    policy_id: str,
    engine: PolicyEngine = Depends(get_policy_engine),
) -> dict[str, Any]:
    # Returns known policy definition or general rule
    return {
        "policy_id": policy_id,
        "name": f"Policy {policy_id}",
        "description": "Financial fraud mitigation and risk governance policy.",
        "status": "active",
        "graphrag_enabled": engine.settings.graphrag_enabled,
    }