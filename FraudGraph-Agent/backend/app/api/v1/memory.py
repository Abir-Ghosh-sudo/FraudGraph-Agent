from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field


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

    query: str | None = Field(
        default=None,
        min_length=1,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
    )


class MemoryReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_id: str

    case_id: str

    similarity: float = Field(
        ge=0.0,
        le=1.0,
    )

    relevance_reason: str | None = None

    outcome: str | None = None

    findings: list[str] = Field(
        default_factory=list,
    )

    decisions: list[str] = Field(
        default_factory=list,
    )


class MemorySearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memories: list[MemoryReference] = Field(
        default_factory=list,
    )

    query: str | None = None

    total: int = Field(
        default=0,
        ge=0,
    )


class MemoryWriteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str

    investigation_id: str

    outcome: str | None = None

    findings: list[str] = Field(
        default_factory=list,
    )

    decisions: list[str] = Field(
        default_factory=list,
    )

    actions: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


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
) -> MemorySearchResult:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Case memory service is not configured yet.",
    )


@router.post(
    "",
    response_model=MemoryWriteResult,
    status_code=status.HTTP_201_CREATED,
)
async def write_memory(
    payload: MemoryWriteRequest,
) -> MemoryWriteResult:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Case memory service is not configured yet.",
    )


@router.get(
    "/{memory_id}",
    response_model=MemoryReference,
)
async def get_memory(
    memory_id: str,
) -> MemoryReference:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Case memory service is not configured yet.",
    )