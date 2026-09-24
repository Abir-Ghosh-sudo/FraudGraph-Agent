from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CaseEvidenceStore:
    """In-memory evidence store for case management."""

    def __init__(self) -> None:
        self._evidence: dict[str, list[Any]] = {}

    def add(self, case_id: str, evidence: Any) -> Any:
        """Add an evidence item for a case."""
        if not case_id:
            raise ValueError("case_id is required")
        self._evidence.setdefault(case_id, []).append(evidence)
        return evidence

    def add_many(self, case_id: str, evidence_items: Iterable[Any]) -> list[Any]:
        """Add multiple evidence items for a case."""
        added = []
        for item in evidence_items:
            added.append(self.add(case_id, item))
        return added

    def list_for_case(self, case_id: str) -> list[Any]:
        """List all evidence recorded for a case."""
        return list(self._evidence.get(case_id, []))

    def count(self, case_id: str | None = None) -> int:
        if case_id is None:
            return sum(len(items) for items in self._evidence.values())
        return len(self._evidence.get(case_id, []))

    def clear_case(self, case_id: str) -> int:
        removed = len(self._evidence.get(case_id, []))
        self._evidence.pop(case_id, None)
        return removed