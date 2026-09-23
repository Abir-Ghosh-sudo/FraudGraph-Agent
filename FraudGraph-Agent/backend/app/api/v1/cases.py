from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.dependencies import get_case_service
from backend.app.errors import CaseNotFoundError, CaseStatusTransitionError
from backend.app.schemas.case import (
    Case,
    CaseAction,
    CaseCreate,
    CaseDecision,
    CaseFinding,
    CaseOutcome,
    CaseStatus,
    CaseUpdate,
)
from backend.app.schemas.investigation import RiskLevel
from backend.app.services.case import CaseService

router = APIRouter(
    prefix="/cases",
    tags=["cases"],
)


@router.post(
    "",
    response_model=Case,
    status_code=status.HTTP_201_CREATED,
)
async def create_case(
    payload: CaseCreate,
    service: CaseService = Depends(get_case_service),
) -> Case:
    return service.create(payload)


@router.get(
    "",
    response_model=list[Case],
)
async def list_cases(
    status_filter: CaseStatus | None = Query(None, alias="status"),
    risk_level: RiskLevel | None = Query(None, alias="risk_level"),
    service: CaseService = Depends(get_case_service),
) -> list[Case]:
    return service.list(status=status_filter, risk_level=risk_level)


@router.get(
    "/{case_id}",
    response_model=Case,
)
async def get_case(
    case_id: str,
    service: CaseService = Depends(get_case_service),
) -> Case:
    case = service.get(case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )
    return case


@router.patch(
    "/{case_id}",
    response_model=Case,
)
async def update_case(
    case_id: str,
    payload: CaseUpdate,
    service: CaseService = Depends(get_case_service),
) -> Case:
    try:
        return service.update(case_id, payload)
    except CaseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )
    except CaseStatusTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.post(
    "/{case_id}/findings",
    response_model=Case,
)
async def add_finding(
    case_id: str,
    finding: CaseFinding,
    service: CaseService = Depends(get_case_service),
) -> Case:
    try:
        return service.add_finding(case_id, finding)
    except CaseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )


@router.post(
    "/{case_id}/decisions",
    response_model=Case,
)
async def add_decision(
    case_id: str,
    decision: CaseDecision,
    service: CaseService = Depends(get_case_service),
) -> Case:
    try:
        return service.add_decision(case_id, decision)
    except CaseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )


@router.post(
    "/{case_id}/actions",
    response_model=Case,
)
async def add_action(
    case_id: str,
    action: CaseAction,
    service: CaseService = Depends(get_case_service),
) -> Case:
    try:
        return service.add_action(case_id, action)
    except CaseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )


@router.post(
    "/{case_id}/outcome",
    response_model=Case,
)
async def set_outcome(
    case_id: str,
    outcome: CaseOutcome,
    rationale: str | None = None,
    service: CaseService = Depends(get_case_service),
) -> Case:
    try:
        return service.set_outcome(case_id, outcome, rationale)
    except CaseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )