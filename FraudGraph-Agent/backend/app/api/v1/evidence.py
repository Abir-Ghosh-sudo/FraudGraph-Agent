from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.dependencies import get_evidence_service
from backend.app.errors import EvidenceNotFoundError
from backend.app.schemas.evidence import (
    Evidence,
    EvidenceCreate,
)
from backend.app.services.evidence import EvidenceService

router = APIRouter(
    prefix="/evidence",
    tags=["evidence"],
)


@router.post(
    "",
    response_model=Evidence,
    status_code=status.HTTP_201_CREATED,
)
async def create_evidence(
    payload: EvidenceCreate,
    investigation_id: str | None = Query(None),
    service: EvidenceService = Depends(get_evidence_service),
) -> Evidence:
    return service.create(payload, investigation_id=investigation_id)


@router.get(
    "",
    response_model=list[Evidence],
)
async def list_evidence(
    investigation_id: str | None = Query(None),
    case_id: str | None = Query(None),
    service: EvidenceService = Depends(get_evidence_service),
) -> list[Evidence]:
    if investigation_id:
        return service.list_for_investigation(investigation_id)
    if case_id:
        return service.list_for_case(case_id)
    return service.list_all()


@router.get(
    "/{evidence_id}",
    response_model=Evidence,
)
async def get_evidence(
    evidence_id: str,
    service: EvidenceService = Depends(get_evidence_service),
) -> Evidence:
    try:
        return service.get(evidence_id)
    except EvidenceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence '{evidence_id}' not found.",
        )


@router.get(
    "/case/{case_id}",
    response_model=list[Evidence],
)
async def list_case_evidence(
    case_id: str,
    service: EvidenceService = Depends(get_evidence_service),
) -> list[Evidence]:
    return service.list_for_case(case_id)


@router.get(
    "/investigation/{investigation_id}",
    response_model=list[Evidence],
)
async def list_investigation_evidence(
    investigation_id: str,
    service: EvidenceService = Depends(get_evidence_service),
) -> list[Evidence]:
    return service.list_for_investigation(investigation_id)