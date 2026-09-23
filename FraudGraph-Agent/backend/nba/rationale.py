from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .candidates import ActionCandidate, ActionType


@dataclass(frozen=True)
class NBARationale:
    """Structured explanation for a next-best-action recommendation."""

    summary: str
    reasoning_points: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    uncertainty_notes: tuple[str, ...]
    approval_reason: str | None
    constraints: tuple[str, ...]


class NBARationaleBuilder:
    """Build transparent, evidence-linked NBA explanations."""

    def build(
        self,
        *,
        selected: ActionCandidate,
        evidence: Iterable[Any] | None = None,
        risk_score: float | None = None,
        risk_level: str | None = None,
        confidence: float | None = None,
        uncertainty: float | None = None,
        requires_approval: bool = False,
        approval_route: str | None = None,
        constraints: Iterable[str] | None = None,
    ) -> NBARationale:
        evidence_items = list(evidence or [])
        constraint_items = tuple(
            str(value) for value in (constraints or ())
        )

        evidence_ids = tuple(
            evidence_id
            for item in evidence_items
            for evidence_id in [self._evidence_id(item)]
            if evidence_id
        )

        reasoning: list[str] = []

        reasoning.append(selected.rationale)

        if risk_level:
            reasoning.append(
                f"Investigation risk level is "
                f"{risk_level.lower()}."
            )

        if risk_score is not None:
            reasoning.append(
                f"Risk score is {self._clamp(risk_score):.2f}."
            )

        if confidence is not None:
            reasoning.append(
                f"Recommendation confidence is "
                f"{self._clamp(confidence):.2f}."
            )

        if evidence_ids:
            reasoning.append(
                f"The recommendation is supported by "
                f"{len(evidence_ids)} linked evidence item(s)."
            )
        else:
            reasoning.append(
                "No explicit evidence identifiers were supplied "
                "for the recommendation."
            )

        uncertainty_notes = self._uncertainty_notes(
            uncertainty=uncertainty,
            selected=selected,
        )

        approval_reason = None

        if requires_approval:
            approval_reason = self._approval_reason(
                selected.action_type,
                approval_route,
            )
            reasoning.append(approval_reason)

        if constraint_items:
            reasoning.append(
                "The recommendation is subject to the "
                "identified investigation constraints."
            )

        summary = self._summary(
            selected=selected,
            risk_level=risk_level,
            requires_approval=requires_approval,
        )

        return NBARationale(
            summary=summary,
            reasoning_points=tuple(reasoning),
            evidence_ids=evidence_ids,
            uncertainty_notes=uncertainty_notes,
            approval_reason=approval_reason,
            constraints=constraint_items,
        )

    def explain(
        self,
        recommendation: Any,
        *,
        evidence: Iterable[Any] | None = None,
    ) -> NBARationale:
        """Build a rationale from an NBARecommendation-like object."""

        selected = self._candidate_from_recommendation(
            recommendation
        )

        return self.build(
            selected=selected,
            evidence=evidence,
            confidence=getattr(
                recommendation,
                "confidence",
                None,
            ),
            requires_approval=bool(
                getattr(
                    recommendation,
                    "requires_approval",
                    False,
                )
            ),
            approval_route=getattr(
                recommendation,
                "approval_route",
                None,
            ),
            constraints=getattr(
                recommendation,
                "constraints",
                (),
            ),
        )

    def _candidate_from_recommendation(
        self,
        recommendation: Any,
    ) -> ActionCandidate:
        action_type = getattr(
            recommendation,
            "action_type",
            ActionType.ESCALATE,
        )

        if not isinstance(action_type, ActionType):
            action_type = ActionType(str(action_type))

        return ActionCandidate(
            action_type=action_type,
            priority=0,
            rationale=str(
                getattr(
                    recommendation,
                    "rationale",
                    "No rationale supplied.",
                )
            ),
            requires_approval=bool(
                getattr(
                    recommendation,
                    "requires_approval",
                    False,
                )
            ),
        )

    def _uncertainty_notes(
        self,
        *,
        uncertainty: float | None,
        selected: ActionCandidate,
    ) -> tuple[str, ...]:
        if uncertainty is None:
            return ()

        value = self._clamp(uncertainty)

        if value >= 0.75:
            return (
                "Investigation uncertainty is very high.",
                "Further evidence or analyst review should be considered.",
            )

        if value >= 0.50:
            return (
                "Investigation uncertainty is high.",
                "The recommendation should be treated cautiously.",
            )

        if value >= 0.30:
            return (
                "Some uncertainty remains in the investigation.",
            )

        return (
            f"Uncertainty is compatible with the "
            f"recommended action: {selected.action_type.value}.",
        )

    def _approval_reason(
        self,
        action_type: ActionType,
        approval_route: str | None,
    ) -> str:
        route = approval_route or "an authorized reviewer"

        if action_type in {
            ActionType.BLOCK_TRANSACTION,
            ActionType.BLOCK_ACCOUNT,
        }:
            return (
                f"{action_type.value} is a controlled action and "
                f"requires approval through {route}."
            )

        if action_type == ActionType.FILE_REPORT:
            return (
                f"Regulatory/internal reporting requires the "
                f"applicable review through {route}."
            )

        return (
            f"This action requires approval through {route} "
            f"before execution."
        )

    def _summary(
        self,
        *,
        selected: ActionCandidate,
        risk_level: str | None,
        requires_approval: bool,
    ) -> str:
        action = selected.action_type.value.replace("_", " ")

        if risk_level:
            summary = (
                f"Recommended next action: {action} "
                f"for a {risk_level.lower()}-risk investigation."
            )
        else:
            summary = f"Recommended next action: {action}."

        if requires_approval:
            summary += " Approval is required before execution."

        return summary

    @staticmethod
    def _evidence_id(item: Any) -> str | None:
        if isinstance(item, Mapping):
            value = item.get("evidence_id")
        else:
            value = getattr(item, "evidence_id", None)

        return str(value) if value is not None else None

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))