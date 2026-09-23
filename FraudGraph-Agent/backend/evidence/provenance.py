"""
Evidence provenance tracking.

Keeps a lightweight, auditable record of where evidence came from and
how it entered the investigation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class EvidenceProvenance:
    """Traceability information for a piece of evidence."""

    evidence_id: str
    source: str
    source_reference: str | None = None
    collected_by: str | None = None
    collection_method: str | None = None
    parent_evidence_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        self.evidence_id = str(self.evidence_id)
        self.source = str(self.source)

        self.parent_evidence_ids = list(
            dict.fromkeys(
                str(item)
                for item in self.parent_evidence_ids
                if item
            )
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""
        return {
            "evidence_id": self.evidence_id,
            "source": self.source,
            "source_reference": self.source_reference,
            "collected_by": self.collected_by,
            "collection_method": self.collection_method,
            "parent_evidence_ids": list(self.parent_evidence_ids),
            "metadata": dict(self.metadata),
            "collected_at": self.collected_at.isoformat(),
        }


class ProvenanceStore:
    """In-memory provenance store for the current investigation process."""

    def __init__(
        self,
        records: list[EvidenceProvenance] | None = None,
    ) -> None:
        self._records: dict[str, EvidenceProvenance] = {}

        for record in records or []:
            self.add(record)

    def add(
        self,
        provenance: EvidenceProvenance,
    ) -> EvidenceProvenance:
        """Store provenance idempotently by evidence ID."""
        existing = self._records.get(provenance.evidence_id)

        if existing is not None:
            return existing

        self._records[provenance.evidence_id] = provenance
        return provenance

    def get(
        self,
        evidence_id: str,
    ) -> EvidenceProvenance | None:
        """Retrieve provenance by evidence ID."""
        return self._records.get(str(evidence_id))

    def remove(
        self,
        evidence_id: str,
    ) -> EvidenceProvenance | None:
        """Remove provenance by evidence ID."""
        return self._records.pop(str(evidence_id), None)

    def all(self) -> list[EvidenceProvenance]:
        """Return all stored provenance records."""
        return list(self._records.values())

    def ids(self) -> list[str]:
        """Return all evidence IDs with provenance."""
        return list(self._records.keys())

    def clear(self) -> None:
        """Remove all provenance records."""
        self._records.clear()

    def __len__(self) -> int:
        return len(self._records)

    def lineage(
        self,
        evidence_id: str,
    ) -> list[str]:
        """
        Return the direct parent evidence IDs for an evidence record.
        """
        record = self.get(evidence_id)

        if record is None:
            return []

        return list(record.parent_evidence_ids)

    def add_record(
        self,
        *,
        evidence_id: str,
        source: str,
        source_reference: str | None = None,
        collected_by: str | None = None,
        collection_method: str | None = None,
        parent_evidence_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvidenceProvenance:
        """Create and store a provenance record."""
        provenance = EvidenceProvenance(
            evidence_id=evidence_id,
            source=source,
            source_reference=source_reference,
            collected_by=collected_by,
            collection_method=collection_method,
            parent_evidence_ids=parent_evidence_ids or [],
            metadata=metadata or {},
        )

        return self.add(provenance)