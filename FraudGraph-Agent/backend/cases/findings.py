from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class CaseFinding:
    """A factual finding recorded during a fraud investigation."""

    finding_id: str
    case_id: str
    title: str
    description: str
    finding_type: str = "general"
    evidence_ids: tuple[str, ...] = ()
    confidence: float | None = None
    severity: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "case_id": self.case_id,
            "title": self.title,
            "description": self.description,
            "finding_type": self.finding_type,
            "evidence_ids": list(self.evidence_ids),
            "confidence": self.confidence,
            "severity": self.severity,
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
        }


class CaseFindingStore:
    """Store and retrieve findings associated with investigation cases."""

    def __init__(self) -> None:
        self._findings: dict[str, CaseFinding] = {}
        self._case_index: dict[str, list[str]] = {}

    def add(self, finding: CaseFinding) -> CaseFinding:
        """Persist a finding without duplicating its identifier."""
        existing = self._findings.get(finding.finding_id)

        if existing is not None:
            return existing

        self._findings[finding.finding_id] = finding

        self._case_index.setdefault(
            finding.case_id,
            [],
        ).append(finding.finding_id)

        return finding

    def add_many(
        self,
        findings: list[CaseFinding],
    ) -> list[CaseFinding]:
        return [self.add(finding) for finding in findings]

    def get(self, finding_id: str) -> CaseFinding | None:
        return self._findings.get(finding_id)

    def require(self, finding_id: str) -> CaseFinding:
        finding = self.get(finding_id)

        if finding is None:
            raise KeyError(
                f"Finding not found: {finding_id}"
            )

        return finding

    def list_for_case(
        self,
        case_id: str,
    ) -> list[CaseFinding]:
        return [
            self._findings[finding_id]
            for finding_id in self._case_index.get(case_id, [])
            if finding_id in self._findings
        ]

    def find_by_type(
        self,
        case_id: str,
        finding_type: str,
    ) -> list[CaseFinding]:
        expected = finding_type.lower()

        return [
            finding
            for finding in self.list_for_case(case_id)
            if finding.finding_type.lower() == expected
        ]

    def remove(self, finding_id: str) -> bool:
        finding = self._findings.pop(
            finding_id,
            None,
        )

        if finding is None:
            return False

        case_findings = self._case_index.get(
            finding.case_id,
            [],
        )

        if finding_id in case_findings:
            case_findings.remove(finding_id)

        if not case_findings:
            self._case_index.pop(
                finding.case_id,
                None,
            )

        return True

    def clear_case(self, case_id: str) -> int:
        finding_ids = list(
            self._case_index.get(case_id, [])
        )

        for finding_id in finding_ids:
            self._findings.pop(
                finding_id,
                None,
            )

        self._case_index.pop(
            case_id,
            None,
        )

        return len(finding_ids)

    def count(self, case_id: str | None = None) -> int:
        if case_id is None:
            return len(self._findings)

        return len(
            self._case_index.get(case_id, [])
        )

    def all(self) -> list[CaseFinding]:
        return list(self._findings.values())

    def export_case(
        self,
        case_id: str,
    ) -> list[dict[str, Any]]:
        return [
            finding.to_dict()
            for finding in self.list_for_case(case_id)
        ]