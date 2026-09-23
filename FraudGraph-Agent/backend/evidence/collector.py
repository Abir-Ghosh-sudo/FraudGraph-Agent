"""
Evidence collection and deduplication utilities.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from backend.app.schemas.evidence import Evidence


class EvidenceCollector:
    """Collect, validate, deduplicate, and organize investigation evidence."""

    def __init__(self) -> None:
        self._evidence: dict[str, Evidence] = {}

    def add(self, evidence: Evidence) -> Evidence:
        """Add evidence using its stable evidence_id."""
        evidence_id = str(evidence.evidence_id)

        if evidence_id not in self._evidence:
            self._evidence[evidence_id] = evidence

        return self._evidence[evidence_id]

    def add_many(
        self,
        evidence: Iterable[Evidence],
    ) -> list[Evidence]:
        """Add multiple evidence records."""
        return [self.add(item) for item in evidence]

    def get(self, evidence_id: str) -> Evidence | None:
        """Retrieve evidence by identifier."""
        return self._evidence.get(str(evidence_id))

    def remove(self, evidence_id: str) -> Evidence | None:
        """Remove evidence by identifier."""
        return self._evidence.pop(str(evidence_id), None)

    def all(self) -> list[Evidence]:
        """Return all collected evidence."""
        return list(self._evidence.values())

    def ids(self) -> list[str]:
        """Return all collected evidence identifiers."""
        return list(self._evidence.keys())

    def clear(self) -> None:
        """Clear the current collection."""
        self._evidence.clear()

    def __len__(self) -> int:
        return len(self._evidence)

    def collect_from(
        self,
        source: Any,
    ) -> list[Evidence]:
        """
        Collect Evidence objects from a supported source.

        Supported sources:
        - a single Evidence instance
        - an iterable of Evidence instances
        - mappings containing ``evidence`` or ``items``
        """
        if source is None:
            return []

        if isinstance(source, Evidence):
            return [self.add(source)]

        if isinstance(source, Mapping):
            nested = source.get("evidence")

            if nested is None:
                nested = source.get("items")

            if nested is not None:
                return self.collect_from(nested)

            return []

        if isinstance(source, (str, bytes)):
            return []

        if isinstance(source, Iterable):
            collected: list[Evidence] = []

            for item in source:
                if isinstance(item, Evidence):
                    collected.append(self.add(item))

            return collected

        return []

    def filter(
        self,
        *,
        source_type: Any | None = None,
        evidence_type: Any | None = None,
        strength: Any | None = None,
    ) -> list[Evidence]:
        """Filter collected evidence by its classification fields."""
        result = self.all()

        if source_type is not None:
            result = [
                item
                for item in result
                if item.source_type == source_type
            ]

        if evidence_type is not None:
            result = [
                item
                for item in result
                if item.evidence_type == evidence_type
            ]

        if strength is not None:
            result = [
                item
                for item in result
                if item.strength == strength
            ]

        return result

    def merge(
        self,
        evidence: Iterable[Evidence],
    ) -> list[Evidence]:
        """
        Merge externally collected evidence into the current collection.

        Existing evidence IDs are preserved, making repeated ingestion
        idempotent.
        """
        return self.add_many(evidence)

    def as_dict(self) -> dict[str, Evidence]:
        """Return evidence keyed by evidence_id."""
        return dict(self._evidence)

    @staticmethod
    def validate(
        evidence: Any,
    ) -> bool:
        """Return True when the supplied object is a valid Evidence model."""
        return isinstance(evidence, Evidence)