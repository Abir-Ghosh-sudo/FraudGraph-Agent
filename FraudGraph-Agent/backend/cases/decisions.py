from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class CaseDecision:
    """A recorded decision made during a fraud investigation."""

    decision_id: str
    case_id: str
    decision: str
    rationale: str
    evidence_ids: tuple[str, ...] = ()
    action: str | None = None
    confidence: float | None = None
    approved: bool = False
    approved_by: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "case_id": self.case_id,
            "decision": self.decision,
            "rationale": self.rationale,
            "evidence_ids": list(self.evidence_ids),
            "action": self.action,
            "confidence": self.confidence,
            "approved": self.approved,
            "approved_by": self.approved_by,
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
        }


class CaseDecisionStore:
    """In-memory decision store used by the case layer."""

    def __init__(self) -> None:
        self._decisions: dict[str, CaseDecision] = {}
        self._case_index: dict[str, list[str]] = {}

    def add(self, decision: CaseDecision) -> CaseDecision:
        """Persist a decision and associate it with its case."""
        existing = self._decisions.get(decision.decision_id)

        if existing is not None:
            return existing

        self._decisions[decision.decision_id] = decision

        self._case_index.setdefault(
            decision.case_id,
            [],
        ).append(decision.decision_id)

        return decision

    def get(self, decision_id: str) -> CaseDecision | None:
        return self._decisions.get(decision_id)

    def require(self, decision_id: str) -> CaseDecision:
        decision = self.get(decision_id)

        if decision is None:
            raise KeyError(
                f"Decision not found: {decision_id}"
            )

        return decision

    def list_for_case(
        self,
        case_id: str,
    ) -> list[CaseDecision]:
        return [
            self._decisions[decision_id]
            for decision_id in self._case_index.get(case_id, [])
            if decision_id in self._decisions
        ]

    def latest(self, case_id: str) -> CaseDecision | None:
        decisions = self.list_for_case(case_id)

        if not decisions:
            return None

        return max(
            decisions,
            key=lambda item: item.created_at,
        )

    def remove(self, decision_id: str) -> bool:
        decision = self._decisions.pop(
            decision_id,
            None,
        )

        if decision is None:
            return False

        case_decisions = self._case_index.get(
            decision.case_id,
            [],
        )

        if decision_id in case_decisions:
            case_decisions.remove(decision_id)

        if not case_decisions:
            self._case_index.pop(
                decision.case_id,
                None,
            )

        return True

    def clear_case(self, case_id: str) -> int:
        decision_ids = list(
            self._case_index.get(case_id, [])
        )

        for decision_id in decision_ids:
            self._decisions.pop(
                decision_id,
                None,
            )

        self._case_index.pop(case_id, None)

        return len(decision_ids)

    def count(self, case_id: str | None = None) -> int:
        if case_id is None:
            return len(self._decisions)

        return len(self._case_index.get(case_id, []))

    def all(self) -> list[CaseDecision]:
        return list(self._decisions.values())