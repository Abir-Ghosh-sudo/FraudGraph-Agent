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
from backend.app.schemas.agent import AgentEvent as _AgentEvent
from backend.app.schemas.agent import AgentEventType, AgentStage

# Derived from the schema so the accepted sets can never drift from it.
_EVENT_TYPES = {member.value for member in AgentEventType}
_STAGES = {member.value for member in AgentStage}

# Upper-case node spellings mapped onto the canonical event type.
_EVENT_TYPE_FALLBACK = {
    "stage_started": "stage_started",
    "investigation_started": "investigation_started",
    "investigation_triggered": "investigation_started",
    "investigation_completed": "investigation_completed",
    "investigation_failed": "investigation_failed",
    "evidence_found": "evidence_found",
    "pattern_detected": "pattern_detected",
    "risk_assessed": "risk_assessed",
    "uncertainty_assessed": "uncertainty_assessed",
    "evidence_requested": "evidence_requested",
    "additional_evidence_requested": "evidence_requested",
    "action_recommended": "action_recommended",
    "approval_requested": "approval_requested",
    "action_executed": "action_executed",
    "action_failed": "action_failed",
    "case_created": "case_updated",
    "case_updated": "case_updated",
    "memory_stored": "memory_updated",
    "memory_updated": "memory_updated",
}
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
    return _normalise_events(
        investigation_id=investigation_id,
        events=service.get_events(investigation_id),
    )


def _normalise_events(
    *,
    investigation_id: str,
    events: list[Any],
) -> list[AgentEvent]:
    """Coerce raw agent events into the AgentEvent response model.

    The workflow nodes emit stage and event names in upper case
    ("STAGE_STARTED", "ASSESS_RISK") and omit investigation_id, while
    AgentEvent declares lower-case enums and requires the id. Serialising the
    raw dicts raised a ResponseValidationError, so GET /events returned 500
    and the audit trail was unreadable.
    """
    normalised: list[AgentEvent] = []

    for raw in events:
        if isinstance(raw, AgentEvent):
            normalised.append(raw)
            continue

        data = raw if isinstance(raw, dict) else getattr(raw, "__dict__", {})
        if not isinstance(data, dict):
            continue

        payload = dict(data)

        event_type = str(payload.get("event_type", "")).strip().lower()
        stage = str(payload.get("stage", "")).strip().lower()

        if event_type not in _EVENT_TYPES:
            event_type = _EVENT_TYPE_FALLBACK.get(
                event_type,
                "stage_started" if stage else "investigation_started",
            )
        if stage not in _STAGES:
            stage = "investigate"

        # RiskLevel/Stage enums are string enums; store the plain value.
        risk_level = payload.get("risk_level")
        if risk_level is not None and not isinstance(risk_level, str):
            risk_level = getattr(risk_level, "value", str(risk_level))

        normalised.append(
            AgentEvent(
                event_id=str(
                    payload.get("event_id")
                    or payload.get("id")
                    or f"{investigation_id}:{len(normalised)}"
                ),
                investigation_id=str(
                    payload.get("investigation_id") or investigation_id
                ),
                event_type=event_type,
                stage=stage,
                message=str(payload.get("message", "")),
                payload=(
                    payload.get("payload")
                    if isinstance(payload.get("payload"), dict)
                    else {}
                ),
                created_at=payload.get("created_at"),
            )
        )

    return normalised


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