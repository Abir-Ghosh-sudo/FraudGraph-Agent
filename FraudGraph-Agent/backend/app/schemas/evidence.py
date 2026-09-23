from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceSourceType(StrEnum):
    TRANSACTION = "transaction"
    GRAPH = "graph"
    CUSTOMER = "customer"
    ACCOUNT = "account"
    DEVICE = "device"
    CONNECTION = "connection"
    HISTORICAL_CASE = "historical_case"
    DOCUMENT = "document"
    POLICY = "policy"
    REGULATION = "regulation"
    EXTERNAL = "external"
    ANALYST = "analyst"


class EvidenceType(StrEnum):
    DIRECT = "direct"
    DERIVED = "derived"
    CORROBORATING = "corroborating"
    CONTRADICTING = "contradicting"
    CONTEXTUAL = "contextual"


class EvidenceStrength(StrEnum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str

    source_type: EvidenceSourceType

    evidence_type: EvidenceType

    title: str = Field(
        min_length=1,
        max_length=300,
    )

    description: str = Field(
        min_length=1,
    )

    source_id: str | None = None

    source_reference: str | None = None

    source_uri: str | None = None

    strength: EvidenceStrength = EvidenceStrength.MODERATE

    reliability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    relevance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    entities: list[str] = Field(
        default_factory=list,
    )

    transaction_ids: list[str] = Field(
        default_factory=list,
    )

    case_ids: list[str] = Field(
        default_factory=list,
    )

    supporting_evidence_ids: list[str] = Field(
        default_factory=list,
    )

    contradicting_evidence_ids: list[str] = Field(
        default_factory=list,
    )

    provenance: dict[str, Any] = Field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )


class EvidenceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: EvidenceSourceType

    evidence_type: EvidenceType

    title: str = Field(
        min_length=1,
        max_length=300,
    )

    description: str = Field(
        min_length=1,
    )

    source_id: str | None = None

    source_reference: str | None = None

    source_uri: str | None = None

    entities: list[str] = Field(
        default_factory=list,
    )

    transaction_ids: list[str] = Field(
        default_factory=list,
    )

    case_ids: list[str] = Field(
        default_factory=list,
    )

    provenance: dict[str, Any] = Field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class EvidenceAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strength: EvidenceStrength

    reliability: float = Field(
        ge=0.0,
        le=1.0,
    )

    relevance: float = Field(
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    explanation: str = Field(
        min_length=1,
    )


class EvidenceCollectionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence: list[Evidence] = Field(
        default_factory=list,
    )

    collected_count: int = Field(
        default=0,
        ge=0,
    )

    collection_sources: list[EvidenceSourceType] = Field(
        default_factory=list,
    )

    complete: bool = False

    missing_sources: list[EvidenceSourceType] = Field(
        default_factory=list,
    )

    rationale: str | None = None