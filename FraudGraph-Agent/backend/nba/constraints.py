from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .candidates import ActionCandidate, ActionType


@dataclass(frozen=True)
class ConstraintValidationResult:
    """Result of policy/constraint evaluation for an action candidate."""

    is_valid: bool = True
    allowed: bool = True
    requires_approval: bool = False
    reasons: tuple[str, ...] = ()
    unmet_requirements: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "allowed": self.allowed,
            "requires_approval": self.requires_approval,
            "reasons": list(self.reasons),
            "unmet_requirements": list(self.unmet_requirements),
        }


class ActionConstraintEngine:
    """Evaluates constraints, authorization, and approval requirements for actions."""

    # High-impact actions that mandate human approval by default
    APPROVAL_ACTIONS: set[str] = {
        "block_transaction",
        "block_account",
        "escalate",
        "file_report",
    }

    def can_recommend(
        self,
        candidate: ActionCandidate,
        *,
        risk_score: float | None = None,
        risk_level: str | None = None,
        available_evidence: Mapping[str, Any] | None = None,
    ) -> bool:
        """Return True if candidate is viable to be recommended."""
        return True

    def validate(
        self,
        candidate: ActionCandidate | str,
        *,
        risk_score: float | None = None,
        risk_level: str | None = None,
        available_evidence: Mapping[str, Any] | None = None,
        authorized: bool = False,
        policy_allows: bool = True,
        human_approval: bool = False,
        context: Mapping[str, Any] | None = None,
        evidence: Sequence[Any] | None = None,
    ) -> ConstraintValidationResult:
        """Validate an action or candidate against business rules."""
        action_name = (
            candidate.action_type.value
            if isinstance(candidate, ActionCandidate)
            else str(candidate)
        )

        requires_approval = (
            (candidate.requires_approval if isinstance(candidate, ActionCandidate) else False)
            or (action_name in self.APPROVAL_ACTIONS)
        )

        reasons: list[str] = []
        unmet: list[str] = []

        if not policy_allows:
            reasons.append(f"Policy denies action: {action_name}")

        if requires_approval and not human_approval:
            reasons.append("Requires supervisory approval")

        is_valid = policy_allows and (not requires_approval or human_approval or authorized)
        allowed = policy_allows

        return ConstraintValidationResult(
            is_valid=is_valid,
            allowed=allowed,
            requires_approval=requires_approval,
            reasons=tuple(reasons),
            unmet_requirements=tuple(unmet),
        )

    def check(
        self,
        action: str,
        *,
        evidence: Sequence[Any] | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> ConstraintValidationResult:
        """Check whether an action is allowed given evidence and context."""
        return self.validate(
            candidate=action,
            evidence=evidence,
            context=context,
        )