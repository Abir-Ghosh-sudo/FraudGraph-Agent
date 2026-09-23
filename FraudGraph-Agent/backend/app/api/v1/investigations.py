from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from backend.agent.state import AgentRuntimeState
from backend.app.dependencies import (
    get_investigation_service,
    get_stream_manager,
)
from backend.app.errors import InvestigationNotFoundError
from backend.app.schemas.agent import AgentEvent
from backend.app.schemas.investigation import (
    Investigation,
    InvestigationCreate,
    InvestigationProgress,
    InvestigationResult,
)
from backend.app.services.investigation import InvestigationService
from backend.app.streaming import EventStreamManager

router = APIRouter(
    prefix="/investigations",
    tags=["investigations"],
)


@router.post(
    "",
    response_model=Investigation,
    status_code=status.HTTP_201_CREATED,
)
async def create_investigation(
    payload: InvestigationCreate,
    service: InvestigationService = Depends(get_investigation_service),
) -> Investigation:
    return service.create(payload)


@router.get(
    "",
    response_model=list[Investigation],
)
async def list_investigations(
    service: InvestigationService = Depends(get_investigation_service),
) -> list[Investigation]:
    return service.list()


@router.get(
    "/{investigation_id}",
    response_model=Investigation,
)
async def get_investigation(
    investigation_id: str,
    service: InvestigationService = Depends(get_investigation_service),
) -> Investigation:
    investigation = service.get(investigation_id)
    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation '{investigation_id}' not found.",
        )
    return investigation


@router.post(
    "/{investigation_id}/start",
    response_model=Investigation,
)
async def start_investigation(
    investigation_id: str,
    service: InvestigationService = Depends(get_investigation_service),
) -> Investigation:
    try:
        return await service.astart(investigation_id)
    except InvestigationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation '{investigation_id}' not found.",
        )


@router.get(
    "/{investigation_id}/progress",
    response_model=InvestigationProgress,
)
async def get_investigation_progress(
    investigation_id: str,
    service: InvestigationService = Depends(get_investigation_service),
) -> InvestigationProgress:
    investigation = service.get(investigation_id)
    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation '{investigation_id}' not found.",
        )
    return investigation.progress


@router.get(
    "/{investigation_id}/result",
    response_model=InvestigationResult,
)
async def get_investigation_result(
    investigation_id: str,
    service: InvestigationService = Depends(get_investigation_service),
) -> InvestigationResult:
    result = service.get_result(investigation_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result for investigation '{investigation_id}' not found.",
        )
    return result


@router.get(
    "/{investigation_id}/events",
    response_model=list[AgentEvent],
)
async def get_investigation_events(
    investigation_id: str,
    service: InvestigationService = Depends(get_investigation_service),
) -> list[AgentEvent]:
    investigation = service.get(investigation_id)
    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation '{investigation_id}' not found.",
        )
    return service.get_events(investigation_id)


@router.get(
    "/{investigation_id}/events/stream",
)
async def stream_investigation_events(
    investigation_id: str,
    service: InvestigationService = Depends(get_investigation_service),
    stream_manager: EventStreamManager = Depends(get_stream_manager),
) -> StreamingResponse:
    investigation = service.get(investigation_id)
    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation '{investigation_id}' not found.",
        )
    return StreamingResponse(
        stream_manager.subscribe(investigation_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )