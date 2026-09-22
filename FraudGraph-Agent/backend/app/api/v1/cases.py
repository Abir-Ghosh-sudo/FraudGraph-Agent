from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.case import (
    Case,
    CaseCreate,
    CaseUpdate,
)


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
) -> Case:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Case persistence service is not configured yet.",
    )


@router.get(
    "",
    response_model=list[Case],
)
async def list_cases() -> list[Case]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Case persistence service is not configured yet.",
    )


@router.get(
    "/{case_id}",
    response_model=Case,
)
async def get_case(
    case_id: str,
) -> Case:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Case persistence service is not configured yet.",
    )


@router.patch(
    "/{case_id}",
    response_model=Case,
)
async def update_case(
    case_id: str,
    payload: CaseUpdate,
) -> Case:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Case persistence service is not configured yet.",
    )