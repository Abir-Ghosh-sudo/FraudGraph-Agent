from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .decisions import CaseDecision, CaseDecisionStore
from .evidence import CaseEvidenceStore
from .findings import CaseFinding, CaseFindingStore
from .lifecycle import CaseLifecycle, CaseStatus


@dataclass(frozen=True)
class CaseSnapshot:
    """Current aggregated state of an investigation case."""

    case_id: str
    status: CaseStatus
    evidence: tuple[Any, ...]
    findings: tuple[CaseFinding, ...]
    decisions: tuple[CaseDecision, ...]
    latest_decision: CaseDecision | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "status": self.status.value,
            "evidence": [
                self._serialize(item)
                for item in self.evidence
            ],
            "findings": [
                item.to_dict()
                for item in self.findings
            ],
            "decisions": [
                item.to_dict()
                for item in self.decisions
            ],
            "latest_decision": (
                self.latest_decision.to_dict()
                if self.latest_decision
                else None
            ),
        }

    @staticmethod
    def _serialize(value: Any) -> Any:
        if hasattr(value, "model_dump"):
            return value.model_dump()

        if hasattr(value, "to_dict"):
            return value.to_dict()

        if isinstance(value, Mapping):
            return dict(value)

        return value


class CaseService:
    """Coordinate case lifecycle, evidence, findings and decisions."""

    def __init__(
        self,
        *,
        evidence_store: CaseEvidenceStore | None = None,
        finding_store: CaseFindingStore | None = None,
        decision_store: CaseDecisionStore | None = None,
    ) -> None:
        self.evidence_store = (
            evidence_store or CaseEvidenceStore()
        )
        self.finding_store = (
            finding_store or CaseFindingStore()
        )
        self.decision_store = (
            decision_store or CaseDecisionStore()
        )
        self._lifecycles: dict[str, CaseLifecycle] = {}

    def create(
        self,
        case_id: str,
    ) -> CaseLifecycle:
        """Create or return the lifecycle for a case."""
        if not case_id.strip():
            raise ValueError("case_id is required.")

        existing = self._lifecycles.get(case_id)

        if existing is not None:
            return existing

        lifecycle = CaseLifecycle(case_id=case_id)
        self._lifecycles[case_id] = lifecycle

        return lifecycle

    def get(
        self,
        case_id: str,
    ) -> CaseLifecycle | None:
        return self._lifecycles.get(case_id)

    def require(
        self,
        case_id: str,
    ) -> CaseLifecycle:
        lifecycle = self.get(case_id)

        if lifecycle is None:
            raise KeyError(
                f"Case not found: {case_id}"
            )

        return lifecycle

    def transition(
        self,
        case_id: str,
        status: CaseStatus | str,
        *,
        reason: str,
        actor: str = "agent",
    ) -> CaseLifecycle:
        lifecycle = self.require(case_id)

        lifecycle.transition(
            status,
            reason=reason,
            actor=actor,
        )

        return lifecycle

    def add_evidence(
        self,
        case_id: str,
        evidence: Any,
    ) -> Any:
        self._ensure_case(case_id)
        return self.evidence_store.add(
            case_id,
            evidence,
        )

    def add_evidence_many(
        self,
        case_id: str,
        evidence: Iterable[Any],
    ) -> list[Any]:
        self._ensure_case(case_id)

        return self.evidence_store.add_many(
            case_id,
            evidence,
        )

    def add_finding(
        self,
        finding: CaseFinding,
    ) -> CaseFinding:
        self._ensure_case(finding.case_id)
        return self.finding_store.add(finding)

    def add_findings(
        self,
        findings: Iterable[CaseFinding],
    ) -> list[CaseFinding]:
        result: list[CaseFinding] = []

        for finding in findings:
            result.append(
                self.add_finding(finding)
            )

        return result

    def add_decision(
        self,
        decision: CaseDecision,
    ) -> CaseDecision:
        self._ensure_case(decision.case_id)
        return self.decision_store.add(decision)

    def snapshot(
        self,
        case_id: str,
    ) -> CaseSnapshot:
        lifecycle = self.require(case_id)

        decisions = tuple(
            self.decision_store.list_for_case(case_id)
        )

        return CaseSnapshot(
            case_id=case_id,
            status=lifecycle.status,
            evidence=tuple(
                self.evidence_store.list_for_case(case_id)
            ),
            findings=tuple(
                self.finding_store.list_for_case(case_id)
            ),
            decisions=decisions,
            latest_decision=self.decision_store.latest(
                case_id
            ),
        )

    def close(
        self,
        case_id: str,
        *,
        reason: str,
        actor: str = "agent",
    ) -> CaseLifecycle:
        return self.transition(
            case_id,
            CaseStatus.CLOSED,
            reason=reason,
            actor=actor,
        )

    def escalate(
        self,
        case_id: str,
        *,
        reason: str,
        actor: str = "agent",
    ) -> CaseLifecycle:
        return self.transition(
            case_id,
            CaseStatus.ESCALATED,
            reason=reason,
            actor=actor,
        )

    def mark_awaiting_evidence(
        self,
        case_id: str,
        *,
        reason: str,
        actor: str = "agent",
    ) -> CaseLifecycle:
        return self.transition(
            case_id,
            CaseStatus.AWAITING_EVIDENCE,
            reason=reason,
            actor=actor,
        )

    def mark_action_recommended(
        self,
        case_id: str,
        *,
        reason: str,
        actor: str = "agent",
    ) -> CaseLifecycle:
        return self.transition(
            case_id,
            CaseStatus.ACTION_RECOMMENDED,
            reason=reason,
            actor=actor,
        )

    def mark_awaiting_approval(
        self,
        case_id: str,
        *,
        reason: str,
        actor: str = "agent",
    ) -> CaseLifecycle:
        return self.transition(
            case_id,
            CaseStatus.AWAITING_APPROVAL,
            reason=reason,
            actor=actor,
        )

    def mark_action_executed(
        self,
        case_id: str,
        *,
        reason: str,
        actor: str = "system",
    ) -> CaseLifecycle:
        return self.transition(
            case_id,
            CaseStatus.ACTION_EXECUTED,
            reason=reason,
            actor=actor,
        )

    def counts(
        self,
        case_id: str,
    ) -> dict[str, int]:
        self.require(case_id)

        return {
            "evidence": self.evidence_store.count(case_id),
            "findings": self.finding_store.count(case_id),
            "decisions": self.decision_store.count(case_id),
        }

    def export(
        self,
        case_id: str,
    ) -> dict[str, Any]:
        """Export the complete in-memory case representation."""
        snapshot = self.snapshot(case_id)
        lifecycle = self.require(case_id)

        return {
            "case": snapshot.to_dict(),
            "lifecycle": lifecycle.export(),
            "counts": self.counts(case_id),
        }

    def remove(
        self,
        case_id: str,
    ) -> bool:
        """Remove a case and its associated in-memory records."""
        existed = case_id in self._lifecycles

        if not existed:
            return False

        self.evidence_store.clear_case(case_id)
        self.finding_store.clear_case(case_id)
        self.decision_store.clear_case(case_id)

        del self._lifecycles[case_id]

        return True

    def _ensure_case(
        self,
        case_id: str,
    ) -> CaseLifecycle:
        existing = self.get(case_id)

        if existing is not None:
            return existing

        return self.create(case_id)