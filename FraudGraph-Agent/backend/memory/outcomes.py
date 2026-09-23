from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class CaseOutcome:
    """Outcome recorded after an investigation reaches a decision."""

    case_id: str
    outcome: str
    action: str | None = None
    fraud_confirmed: bool | None = None
    risk_level: str | None = None
    findings: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    analyst_decision: str | None = None
    notes: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "outcome": self.outcome,
            "action": self.action,
            "fraud_confirmed": self.fraud_confirmed,
            "risk_level": self.risk_level,
            "findings": list(self.findings),
            "evidence_ids": list(self.evidence_ids),
            "analyst_decision": self.analyst_decision,
            "notes": self.notes,
            "metadata": dict(self.metadata),
            "recorded_at": self.recorded_at.isoformat(),
        }


class OutcomeStore:
    """Store and retrieve investigation outcomes for case memory."""

    def __init__(self) -> None:
        self._outcomes: dict[str, list[CaseOutcome]] = {}

    def add(self, outcome: CaseOutcome) -> CaseOutcome:
        outcomes = self._outcomes.setdefault(
            outcome.case_id,
            [],
        )

        for existing in outcomes:
            if (
                existing.outcome == outcome.outcome
                and existing.recorded_at == outcome.recorded_at
            ):
                return existing

        outcomes.append(outcome)
        outcomes.sort(key=lambda item: item.recorded_at)

        return outcome

    def record(
        self,
        *,
        case_id: str,
        outcome: str,
        action: str | None = None,
        fraud_confirmed: bool | None = None,
        risk_level: str | None = None,
        findings: list[str] | tuple[str, ...] | None = None,
        evidence_ids: list[str] | tuple[str, ...] | None = None,
        analyst_decision: str | None = None,
        notes: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CaseOutcome:
        result = CaseOutcome(
            case_id=case_id,
            outcome=outcome,
            action=action,
            fraud_confirmed=fraud_confirmed,
            risk_level=risk_level,
            findings=tuple(findings or ()),
            evidence_ids=tuple(evidence_ids or ()),
            analyst_decision=analyst_decision,
            notes=notes,
            metadata=dict(metadata or {}),
        )

        return self.add(result)

    def list_for_case(
        self,
        case_id: str,
    ) -> list[CaseOutcome]:
        return list(self._outcomes.get(case_id, []))

    def latest(
        self,
        case_id: str,
    ) -> CaseOutcome | None:
        outcomes = self._outcomes.get(case_id, [])

        if not outcomes:
            return None

        return outcomes[-1]

    def find_by_outcome(
        self,
        outcome: str,
    ) -> list[CaseOutcome]:
        result: list[CaseOutcome] = []

        for outcomes in self._outcomes.values():
            result.extend(
                item
                for item in outcomes
                if item.outcome == outcome
            )

        return result

    def find_by_action(
        self,
        action: str,
    ) -> list[CaseOutcome]:
        result: list[CaseOutcome] = []

        for outcomes in self._outcomes.values():
            result.extend(
                item
                for item in outcomes
                if item.action == action
            )

        return result

    def find_confirmed_fraud(
        self,
    ) -> list[CaseOutcome]:
        result: list[CaseOutcome] = []

        for outcomes in self._outcomes.values():
            result.extend(
                item
                for item in outcomes
                if item.fraud_confirmed is True
            )

        return result

    def count(self, case_id: str) -> int:
        return len(self._outcomes.get(case_id, []))

    def clear_case(self, case_id: str) -> None:
        self._outcomes.pop(case_id, None)

    def export(
        self,
        case_id: str,
    ) -> list[dict[str, Any]]:
        return [
            outcome.to_dict()
            for outcome in self.list_for_case(case_id)
        ]