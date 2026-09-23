from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.app.config import Settings
from backend.app.errors import EvidenceNotFoundError
from backend.app.logging import get_logger
from backend.app.schemas.evidence import (
    Evidence,
    EvidenceCreate,
    EvidenceSourceType,
    EvidenceStrength,
    EvidenceType,
)

logger = get_logger(__name__)

_STRENGTH_SCORE: dict[EvidenceStrength, float] = {
    EvidenceStrength.WEAK: 0.25,
    EvidenceStrength.MODERATE: 0.50,
    EvidenceStrength.STRONG: 0.75,
    EvidenceStrength.VERY_STRONG: 1.00,
}


class EvidenceService:
    """
    In-memory evidence store with deduplication and scoring.

    Evidence is keyed by (source_type, source_id, evidence_type) for deduplication.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._evidence: dict[str, Evidence] = {}
        # Maps dedup_key → evidence_id
        self._dedup_index: dict[str, str] = {}
        # Maps investigation_id → set of evidence_ids
        self._investigation_index: dict[str, set[str]] = {}
        # Maps case_id → set of evidence_ids
        self._case_index: dict[str, set[str]] = {}

    def create(
        self,
        payload: EvidenceCreate,
        *,
        investigation_id: str | None = None,
        strength: EvidenceStrength = EvidenceStrength.MODERATE,
        reliability: float = 0.5,
        relevance: float = 0.5,
        confidence: float = 0.5,
    ) -> Evidence:
        now = datetime.now(UTC)

        # Deduplicate by (source_type, source_id, evidence_type)
        dedup_key = _make_dedup_key(
            payload.source_type,
            payload.source_id,
            payload.evidence_type,
        )

        existing_id = self._dedup_index.get(dedup_key)
        if existing_id is not None:
            existing = self._evidence.get(existing_id)
            if existing is not None:
                logger.debug(
                    "evidence deduplicated",
                    existing_id=existing_id,
                    dedup_key=dedup_key,
                )
                if investigation_id:
                    self._investigation_index.setdefault(
                        investigation_id, set()
                    ).add(existing_id)
                return existing

        evidence_id = f"ev_{uuid4().hex[:12]}"

        evidence = Evidence(
            evidence_id=evidence_id,
            source_type=payload.source_type,
            evidence_type=payload.evidence_type,
            title=payload.title,
            description=payload.description,
            source_id=payload.source_id,
            source_reference=payload.source_reference,
            strength=strength,
            reliability=reliability,
            relevance=relevance,
            confidence=confidence,
            entities=payload.entities,
            transaction_ids=payload.transaction_ids,
            case_ids=payload.case_ids,
            provenance=payload.provenance,
            metadata=payload.metadata,
            collected_at=now,
            created_at=now,
        )

        self._evidence[evidence_id] = evidence
        self._dedup_index[dedup_key] = evidence_id

        if investigation_id:
            self._investigation_index.setdefault(
                investigation_id, set()
            ).add(evidence_id)

        for case_id in payload.case_ids:
            self._case_index.setdefault(case_id, set()).add(evidence_id)

        return evidence

    def get(self, evidence_id: str) -> Evidence:
        evidence = self._evidence.get(evidence_id)
        if evidence is None:
            raise EvidenceNotFoundError(f"Evidence '{evidence_id}' not found.")
        return evidence

    def list_for_investigation(
        self,
        investigation_id: str,
    ) -> list[Evidence]:
        ids = self._investigation_index.get(investigation_id, set())
        return [
            self._evidence[eid]
            for eid in ids
            if eid in self._evidence
        ]

    def list_for_case(self, case_id: str) -> list[Evidence]:
        ids = self._case_index.get(case_id, set())
        return [
            self._evidence[eid]
            for eid in ids
            if eid in self._evidence
        ]

    def list_all(self) -> list[Evidence]:
        return list(self._evidence.values())

    def link_to_case(self, evidence_id: str, case_id: str) -> None:
        self._case_index.setdefault(case_id, set()).add(evidence_id)

    def compute_aggregate_score(
        self,
        evidence_ids: list[str],
    ) -> dict[str, float]:
        """
        Compute aggregate risk contribution from a list of evidence items.

        Returns: {risk_contribution, average_confidence, average_reliability}
        """
        items = [
            self._evidence[eid]
            for eid in evidence_ids
            if eid in self._evidence
        ]

        if not items:
            return {
                "risk_contribution": 0.0,
                "average_confidence": 0.0,
                "average_reliability": 0.0,
                "count": 0,
            }

        total_contribution = 0.0
        total_confidence = 0.0
        total_reliability = 0.0

        for item in items:
            strength_score = _STRENGTH_SCORE.get(item.strength, 0.5)
            # Direct/corroborating evidence adds; contradicting subtracts
            if item.evidence_type == EvidenceType.CONTRADICTING:
                contribution = -strength_score * item.confidence
            else:
                contribution = strength_score * item.confidence
            total_contribution += contribution
            total_confidence += item.confidence
            total_reliability += item.reliability

        n = len(items)
        return {
            "risk_contribution": max(0.0, min(1.0, total_contribution / n)),
            "average_confidence": total_confidence / n,
            "average_reliability": total_reliability / n,
            "count": n,
        }

    def get_missing_sources(
        self,
        evidence_ids: list[str],
        required_sources: list[EvidenceSourceType],
    ) -> list[EvidenceSourceType]:
        """Return required source types not represented in current evidence."""
        present_sources = {
            self._evidence[eid].source_type
            for eid in evidence_ids
            if eid in self._evidence
        }
        return [s for s in required_sources if s not in present_sources]


def _make_dedup_key(
    source_type: EvidenceSourceType,
    source_id: str | None,
    evidence_type: EvidenceType,
) -> str:
    return f"{source_type}:{source_id or ''}:{evidence_type}"
