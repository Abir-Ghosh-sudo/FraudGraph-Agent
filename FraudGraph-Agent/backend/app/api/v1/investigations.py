from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.investigation import (
    Investigation,
    InvestigationCreate,
    InvestigationProgress,
    InvestigationStatus,
)


router = APIRouter(
    prefix="/investigations",
    tags=["investigations"],
)


_investigations: dict[str, Investigation] = {}


@router.post(
    "",
    response_model=Investigation,
    status_code=status.HTTP_201_CREATED,
)
async def create_investigation(
    payload: InvestigationCreate,
) -> Investigation:
    now = datetime.now(UTC)
    investigation_id = f"inv_{uuid4().hex}"

    investigation = Investigation(
        investigation_id=investigation_id,
        status=InvestigationStatus.PENDING,
        trigger=payload.trigger,
        progress=InvestigationProgress(),
        created_at=now,
        updated_at=now,
    )

    _investigations[investigation_id] = investigation

    return investigation


@router.get(
    "",
    response_model=list[Investigation],
)
async def list_investigations() -> list[Investigation]:
    return list(_investigations.values())


@router.get(
    "/{investigation_id}",
    response_model=Investigation,
)
async def get_investigation(
    investigation_id: str,
) -> Investigation:
    investigation = _investigations.get(investigation_id)

    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found.",
        )

    return investigation


@router.get(
    "/{investigation_id}/progress",
    response_model=InvestigationProgress,
)
async def get_investigation_progress(
    investigation_id: str,
) -> InvestigationProgress:
    investigation = _investigations.get(investigation_id)

    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found.",
        )

    return investigation.progress