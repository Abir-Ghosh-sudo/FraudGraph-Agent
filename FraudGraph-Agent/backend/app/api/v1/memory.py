from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from backend.app.dependencies import get_memory_service
from backend.app.errors import MemoryNotFoundError
from backend.app.services.memory import MemoryService

router = APIRouter(
    prefix="/memory",
    tags=["memory"],
)


class MemorySearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    investigation_id: str | None = None
    case_id: str | None = None
    customer_id: str | None = None
    transaction_id: str | None = None
    query: str | None = Field(default=None, min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class MemoryReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_id: str
    case_id: str
    similarity: float = Field(ge=0.0, le=1.0)
    relevance_reason: str | None = None
    outcome: str | None = None
    findings: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)


class MemorySearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memories: list[MemoryReference] = Field(default_factory=list)
    query: str | None = None
    total: int = Field(default=0, ge=0)


class MemoryWriteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    investigation_id: str
    outcome: str | None = None
    findings: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryWriteResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_id: str
    case_id: str
    created_at: datetime


@router.post(
    "/search",
    response_model=MemorySearchResult,
)
async def search_memory(
    payload: MemorySearchRequest,
    service: MemoryService = Depends(get_memory_service),
) -> MemorySearchResult:
    context: dict[str, Any] = {}
    if payload.query:
        context["query"] = payload.query
    if payload.case_id:
        context["case_id"] = payload.case_id
    if payload.investigation_id:
        context["investigation_id"] = payload.investigation_id

    results = service.search(context, top_k=payload.top_k)

    memories: list[MemoryReference] = []
    for res in results:
        memories.append(
            MemoryReference(
                memory_id=res.get("memory_id", ""),
                case_id=res.get("case_id", ""),
                similarity=float(res.get("similarity", 0.0)),
                relevance_reason=res.get("relevance_reason") or f"Similarity match: {res.get('similarity', 0.0):.2f}",
                outcome=res.get("outcome"),
                findings=res.get("findings", []),
                decisions=res.get("decisions", []),
            )
        )

    return MemorySearchResult(
        memories=memories,
        query=payload.query,
        total=len(memories),
    )


@router.post(
    "",
    response_model=MemoryWriteResult,
    status_code=status.HTTP_201_CREATED,
)
async def write_memory(
    payload: MemoryWriteRequest,
    service: MemoryService = Depends(get_memory_service),
) -> MemoryWriteResult:
    memory_id = service.store(
        case_id=payload.case_id,
        investigation_id=payload.investigation_id,
        outcome=payload.outcome,
        findings=payload.findings,
        decisions=payload.decisions,
        actions=payload.actions,
        metadata=payload.metadata,
    )
    return MemoryWriteResult(
        memory_id=memory_id,
        case_id=payload.case_id,
        created_at=datetime.now(UTC),
    )


@router.get(
    "/{memory_id}",
    response_model=MemoryReference,
)
async def get_memory(
    memory_id: str,
    service: MemoryService = Depends(get_memory_service),
) -> MemoryReference:
    try:
        entry = service.get(memory_id)
        return MemoryReference(
            memory_id=entry.memory_id,
            case_id=entry.case_id,
            similarity=1.0,
            relevance_reason="Direct lookup",
            outcome=entry.outcome,
            findings=entry.findings,
            decisions=entry.decisions,
        )
    except MemoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory '{memory_id}' not found.",
        )