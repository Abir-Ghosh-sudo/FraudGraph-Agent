from __future__ import annotations

from typing import Any, Iterable

from .outcomes import CaseOutcome, OutcomeStore


class MemoryWriter:
    """Write investigation outcomes and decisions into case memory."""

    def __init__(
        self,
        outcome_store: OutcomeStore | None = None,
    ) -> None:
        self.outcome_store = outcome_store or OutcomeStore()

    def write_outcome(
        self,
        outcome: CaseOutcome,
    ) -> CaseOutcome:
        return self.outcome_store.add(outcome)

    def record_outcome(
        self,
        *,
        case_id: str,
        outcome: str,
        action: str | None = None,
        fraud_confirmed: bool | None = None,
        risk_level: str | None = None,
        findings: Iterable[str] | None = None,
        evidence_ids: Iterable[str] | None = None,
        analyst_decision: str | None = None,
        notes: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CaseOutcome:
        return self.outcome_store.record(
            case_id=case_id,
            outcome=outcome,
            action=action,
            fraud_confirmed=fraud_confirmed,
            risk_level=risk_level,
            findings=tuple(findings or ()),
            evidence_ids=tuple(evidence_ids or ()),
            analyst_decision=analyst_decision,
            notes=notes,
            metadata=metadata,
        )

    def record_decision(
        self,
        *,
        case_id: str,
        decision: str,
        action: str | None = None,
        risk_level: str | None = None,
        fraud_confirmed: bool | None = None,
        findings: Iterable[str] | None = None,
        evidence_ids: Iterable[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CaseOutcome:
        return self.record_outcome(
            case_id=case_id,
            outcome=decision,
            action=action,
            risk_level=risk_level,
            fraud_confirmed=fraud_confirmed,
            findings=findings,
            evidence_ids=evidence_ids,
            metadata=metadata,
        )

    def record_action_result(
        self,
        *,
        case_id: str,
        action: str,
        outcome: str,
        fraud_confirmed: bool | None = None,
        risk_level: str | None = None,
        findings: Iterable[str] | None = None,
        evidence_ids: Iterable[str] | None = None,
        notes: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CaseOutcome:
        return self.record_outcome(
            case_id=case_id,
            outcome=outcome,
            action=action,
            fraud_confirmed=fraud_confirmed,
            risk_level=risk_level,
            findings=findings,
            evidence_ids=evidence_ids,
            notes=notes,
            metadata=metadata,
        )

    def get_latest(
        self,
        case_id: str,
    ) -> CaseOutcome | None:
        return self.outcome_store.latest(case_id)

    def get_history(
        self,
        case_id: str,
    ) -> list[CaseOutcome]:
        return self.outcome_store.list_for_case(case_id)

    def export(
        self,
        case_id: str,
    ) -> list[dict[str, Any]]:
        return self.outcome_store.export(case_id)