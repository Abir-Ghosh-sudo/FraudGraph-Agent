from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.evidence import (
    Evidence,
    EvidenceCreate,
)


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
) -> Evidence:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Evidence persistence service is not configured yet.",
    )


@router.get(
    "/{evidence_id}",
    response_model=Evidence,
)
async def get_evidence(
    evidence_id: str,
) -> Evidence:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Evidence persistence service is not configured yet.",
    )


@router.get(
    "/case/{case_id}",
    response_model=list[Evidence],
)
async def list_case_evidence(
    case_id: str,
) -> list[Evidence]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Evidence persistence service is not configured yet.",
    )


@router.get(
    "/investigation/{investigation_id}",
    response_model=list[Evidence],
)
async def list_investigation_evidence(
    investigation_id: str,
) -> list[Evidence]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Evidence persistence service is not configured yet.",
    )