from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .candidates import ActionCandidate, ActionCandidateFactory, ActionType
from .constraints import ActionConstraintEngine


@dataclass(frozen=True)
class NBARecommendation:
    """Selected next-best-action recommendation."""

    action_type: ActionType
    rationale: str
    confidence: float
    requires_approval: bool
    approval_route: str | None
    alternatives: tuple[ActionCandidate, ...]
    evidence_ids: tuple[str, ...]
    constraints: tuple[str, ...]


class NBAEngine:
    """Select and explain the next best action for an investigation."""

    def __init__(
        self,
        candidate_factory: ActionCandidateFactory | None = None,
        constraint_engine: ActionConstraintEngine | None = None,
    ) -> None:
        self.candidate_factory = (
            candidate_factory or ActionCandidateFactory()
        )
        self.constraint_engine = (
            constraint_engine or ActionConstraintEngine()
        )

    def recommend(
        self,
        *,
        risk_score: float | None = None,
        risk_level: str | None = None,
        evidence: Iterable[Any] | None = None,
        patterns: Iterable[Any] | None = None,
        requires_additional_evidence: bool = False,
        transaction_available: bool = True,
        account_available: bool = True,
        case_available: bool = False,
        authorized: bool = False,
        policy_allows: bool = True,
        human_approval: bool = False,
        context: Mapping[str, Any] | None = None,
    ) -> NBARecommendation:
        """Generate the most appropriate action recommendation."""

        evidence_items = list(evidence or [])
        pattern_items = list(patterns or [])

        evidence_ids = tuple(
            self._evidence_id(item)
            for item in evidence_items
            if self._evidence_id(item)
        )

        available_evidence = self._available_evidence(
            evidence_items,
            context,
        )

        candidates = self.candidate_factory.build(
            risk_level=risk_level,
            risk_score=risk_score,
            requires_additional_evidence=requires_additional_evidence,
            transaction_available=transaction_available,
            account_available=account_available,
            case_available=case_available,
        )

        viable: list[ActionCandidate] = []

        for candidate in candidates:
            if self.constraint_engine.can_recommend(
                candidate,
                risk_score=risk_score,
                risk_level=risk_level,
                available_evidence=available_evidence,
            ):
                viable.append(candidate)

        if not viable:
            fallback = self._fallback_candidate()
            viable = [fallback]

        selected = self._select(
            viable,
            risk_score=risk_score,
            risk_level=risk_level,
            requires_additional_evidence=requires_additional_evidence,
        )

        constraint_result = self.constraint_engine.validate(
            selected,
            risk_score=risk_score,
            risk_level=risk_level,
            available_evidence=available_evidence,
            authorized=authorized,
            policy_allows=policy_allows,
            human_approval=human_approval,
            context=context,
        )

        confidence = self._confidence(
            selected=selected,
            risk_score=risk_score,
            risk_level=risk_level,
            evidence_count=len(evidence_items),
            pattern_count=len(pattern_items),
            requires_additional_evidence=requires_additional_evidence,
        )

        rationale = self._build_rationale(
            selected=selected,
            risk_score=risk_score,
            risk_level=risk_level,
            evidence_count=len(evidence_items),
            pattern_count=len(pattern_items),
            requires_additional_evidence=requires_additional_evidence,
            requires_approval=constraint_result.requires_approval,
        )

        alternatives = tuple(
            candidate
            for candidate in viable
            if candidate.action_type != selected.action_type
        )

        approval_route = self._approval_route(
            selected,
            constraint_result.requires_approval,
        )

        return NBARecommendation(
            action_type=selected.action_type,
            rationale=rationale,
            confidence=confidence,
            requires_approval=constraint_result.requires_approval,
            approval_route=approval_route,
            alternatives=alternatives,
            evidence_ids=evidence_ids,
            constraints=tuple(
                constraint_result.reasons
                + constraint_result.unmet_requirements
            ),
        )

    def rank(
        self,
        candidates: Iterable[ActionCandidate],
        *,
        risk_score: float | None = None,
        risk_level: str | None = None,
        requires_additional_evidence: bool = False,
    ) -> list[ActionCandidate]:
        """Return candidates ordered by investigation context."""

        items = list(candidates)

        def score(candidate: ActionCandidate) -> tuple[int, int]:
            context_bonus = 0

            if requires_additional_evidence:
                if candidate.action_type == ActionType.REQUEST_EVIDENCE:
                    context_bonus += 100

            if risk_level in {"critical", "high"}:
                if candidate.action_type in {
                    ActionType.BLOCK_TRANSACTION,
                    ActionType.BLOCK_ACCOUNT,
                    ActionType.ESCALATE,
                }:
                    context_bonus += 20

            if risk_score is not None and risk_score >= 0.85:
                if candidate.action_type == ActionType.BLOCK_ACCOUNT:
                    context_bonus += 20

            return (
                -(context_bonus),
                candidate.priority,
            )

        return sorted(items, key=score)

    def _select(
        self,
        candidates: list[ActionCandidate],
        *,
        risk_score: float | None,
        risk_level: str | None,
        requires_additional_evidence: bool,
    ) -> ActionCandidate:
        ranked = self.rank(
            candidates,
            risk_score=risk_score,
            risk_level=risk_level,
            requires_additional_evidence=requires_additional_evidence,
        )

        return ranked[0]

    def _fallback_candidate(self) -> ActionCandidate:
        return ActionCandidate(
            action_type=ActionType.ESCALATE,
            priority=1000,
            rationale=(
                "No action candidate satisfied the available "
                "investigation constraints; escalate for review."
            ),
            requires_approval=True,
            required_evidence=(),
            constraints=("manual_review_required",),
        )

    def _available_evidence(
        self,
        evidence: list[Any],
        context: Mapping[str, Any] | None,
    ) -> set[str]:
        available: set[str] = set()

        for item in evidence:
            if isinstance(item, Mapping):
                source = item.get("source_type")
                evidence_type = item.get("evidence_type")
            else:
                source = getattr(item, "source_type", None)
                evidence_type = getattr(item, "evidence_type", None)

            for value in (source, evidence_type):
                if value is not None:
                    available.add(
                        str(getattr(value, "value", value)).lower()
                    )

            evidence_id = self._evidence_id(item)
            if evidence_id:
                available.add(evidence_id)

        if context:
            provided = context.get("available_evidence", ())
            available.update(str(value).lower() for value in provided)

        return available

    def _evidence_id(self, item: Any) -> str | None:
        if isinstance(item, Mapping):
            value = item.get("evidence_id")
        else:
            value = getattr(item, "evidence_id", None)

        return str(value) if value is not None else None

    def _confidence(
        self,
        *,
        selected: ActionCandidate,
        risk_score: float | None,
        risk_level: str | None,
        evidence_count: int,
        pattern_count: int,
        requires_additional_evidence: bool,
    ) -> float:
        score = 0.40

        if evidence_count:
            score += min(0.20, evidence_count * 0.04)

        if pattern_count:
            score += min(0.15, pattern_count * 0.05)

        if risk_score is not None:
            score += self._clamp(risk_score) * 0.15

        if risk_level in {"high", "critical"}:
            score += 0.10

        if requires_additional_evidence:
            score -= 0.20

        if selected.action_type == ActionType.ESCALATE:
            score = min(score, 0.75)

        return self._clamp(score)

    def _build_rationale(
        self,
        *,
        selected: ActionCandidate,
        risk_score: float | None,
        risk_level: str | None,
        evidence_count: int,
        pattern_count: int,
        requires_additional_evidence: bool,
        requires_approval: bool,
    ) -> str:
        parts = [selected.rationale]

        if risk_level:
            parts.append(
                f"Current risk level: {risk_level.lower()}."
            )

        if risk_score is not None:
            parts.append(
                f"Risk score: {self._clamp(risk_score):.2f}."
            )

        parts.append(
            f"Decision considered {evidence_count} evidence item(s) "
            f"and {pattern_count} pattern(s)."
        )

        if requires_additional_evidence:
            parts.append(
                "Additional evidence remains relevant to the decision."
            )

        if requires_approval:
            parts.append(
                "Execution requires the applicable approval route."
            )

        return " ".join(parts)

    def _approval_route(
        self,
        candidate: ActionCandidate,
        requires_approval: bool,
    ) -> str | None:
        if not requires_approval:
            return None

        if candidate.action_type == ActionType.FILE_REPORT:
            return "compliance"

        if candidate.action_type in {
            ActionType.BLOCK_TRANSACTION,
            ActionType.BLOCK_ACCOUNT,
        }:
            return "authorized_fraud_analyst"

        return "fraud_analyst"

    @staticmethod
    def _clamp(value: float | None) -> float:
        if value is None:
            return 0.0

        return max(0.0, min(1.0, float(value)))