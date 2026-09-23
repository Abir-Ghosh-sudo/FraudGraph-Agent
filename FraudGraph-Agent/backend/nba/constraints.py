from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class ActionType(str, Enum):
    """Supported next-best-action types."""

    ALLOW_TRANSACTION = "allow_transaction"
    BLOCK_TRANSACTION = "block_transaction"
    MONITOR_ACCOUNT = "monitor_account"
    BLOCK_ACCOUNT = "block_account"
    WARN_CUSTOMER = "warn_customer"
    CREATE_CASE = "create_case"
    REQUEST_EVIDENCE = "request_evidence"
    ESCALATE = "escalate"
    FILE_REPORT = "file_report"


@dataclass(frozen=True)
class ActionCandidate:
    """A candidate action considered by the NBA engine."""

    action_type: ActionType
    priority: int
    rationale: str
    requires_approval: bool
    required_evidence: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    metadata: Mapping[str, Any] | None = None


class ActionCandidateFactory:
    """Build valid NBA candidates from investigation context."""

    DEFAULT_APPROVAL: dict[ActionType, bool] = {
        ActionType.ALLOW_TRANSACTION: False,
        ActionType.BLOCK_TRANSACTION: True,
        ActionType.MONITOR_ACCOUNT: False,
        ActionType.BLOCK_ACCOUNT: True,
        ActionType.WARN_CUSTOMER: False,
        ActionType.CREATE_CASE: False,
        ActionType.REQUEST_EVIDENCE: False,
        ActionType.ESCALATE: True,
        ActionType.FILE_REPORT: True,
    }

    def build(
        self,
        *,
        risk_level: str | None = None,
        risk_score: float | None = None,
        requires_additional_evidence: bool = False,
        transaction_available: bool = True,
        account_available: bool = True,
        case_available: bool = False,
    ) -> list[ActionCandidate]:
        """Generate action candidates from the current investigation state."""
        level = (risk_level or "unknown").lower()
        score = self._clamp(risk_score)

        candidates: list[ActionCandidate] = []

        if requires_additional_evidence:
            candidates.append(
                self._candidate(
                    ActionType.REQUEST_EVIDENCE,
                    priority=10,
                    rationale=(
                        "Additional evidence is required before a "
                        "defensible enforcement decision can be made."
                    ),
                    required_evidence=(
                        "customer_validation",
                        "step_up_authentication",
                        "analyst_review",
                    ),
                )
            )

        if transaction_available:
            if level in {"critical", "high"} or score >= 0.65:
                candidates.append(
                    self._candidate(
                        ActionType.BLOCK_TRANSACTION,
                        priority=20,
                        rationale=(
                            "Transaction risk is sufficiently elevated "
                            "to consider transaction blocking."
                        ),
                        required_evidence=("risk_assessment",),
                        constraints=("authorized_transaction_control",),
                    )
                )
            else:
                candidates.append(
                    self._candidate(
                        ActionType.ALLOW_TRANSACTION,
                        priority=80,
                        rationale=(
                            "Current evidence does not establish "
                            "sufficient risk for transaction blocking."
                        ),
                        required_evidence=("risk_assessment",),
                    )
                )

        if account_available:
            if level == "critical" or score >= 0.85:
                candidates.append(
                    self._candidate(
                        ActionType.BLOCK_ACCOUNT,
                        priority=30,
                        rationale=(
                            "Critical account-level risk supports "
                            "consideration of account blocking."
                        ),
                        required_evidence=(
                            "risk_assessment",
                            "supporting_fraud_evidence",
                        ),
                        constraints=("authorized_account_control",),
                    )
                )

            candidates.append(
                self._candidate(
                    ActionType.MONITOR_ACCOUNT,
                    priority=60,
                    rationale=(
                        "Account monitoring provides a controlled "
                        "response when continued observation is useful."
                    ),
                    required_evidence=("risk_assessment",),
                )
            )

        if not case_available:
            candidates.append(
                self._candidate(
                    ActionType.CREATE_CASE,
                    priority=40,
                    rationale=(
                        "A persistent investigation case should record "
                        "the evidence, findings, decisions, and actions."
                    ),
                    required_evidence=("investigation_record",),
                )
            )

        if level in {"high", "critical"} or score >= 0.65:
            candidates.append(
                self._candidate(
                    ActionType.WARN_CUSTOMER,
                    priority=50,
                    rationale=(
                        "Elevated risk may justify a customer warning "
                        "through an approved communication channel."
                    ),
                    required_evidence=("risk_assessment",),
                )
            )

            candidates.append(
                self._candidate(
                    ActionType.ESCALATE,
                    priority=35,
                    rationale=(
                        "Elevated risk may require authorized analyst "
                        "or specialist review."
                    ),
                    required_evidence=(
                        "risk_assessment",
                        "investigation_findings",
                    ),
                )
            )

        if level == "critical" or score >= 0.85:
            candidates.append(
                self._candidate(
                    ActionType.FILE_REPORT,
                    priority=45,
                    rationale=(
                        "Critical findings may require regulatory or "
                        "internal reporting subject to policy review."
                    ),
                    required_evidence=(
                        "case_record",
                        "investigation_findings",
                        "policy_assessment",
                    ),
                    constraints=("reporting_policy_check",),
                )
            )

        return self._deduplicate(candidates)

    def from_mapping(
        self,
        data: Mapping[str, Any],
    ) -> ActionCandidate:
        """Create a candidate from a serialized mapping."""
        raw_action = data.get("action_type")

        if raw_action is None:
            raise ValueError("action_type is required")

        try:
            action_type = ActionType(str(raw_action))
        except ValueError as exc:
            raise ValueError(
                f"Unsupported action type: {raw_action}"
            ) from exc

        return ActionCandidate(
            action_type=action_type,
            priority=int(data.get("priority", 100)),
            rationale=str(data.get("rationale", "")),
            requires_approval=bool(
                data.get(
                    "requires_approval",
                    self.DEFAULT_APPROVAL[action_type],
                )
            ),
            required_evidence=tuple(
                str(value)
                for value in data.get("required_evidence", ())
            ),
            constraints=tuple(
                str(value)
                for value in data.get("constraints", ())
            ),
            metadata=data.get("metadata"),
        )

    def _candidate(
        self,
        action_type: ActionType,
        *,
        priority: int,
        rationale: str,
        required_evidence: tuple[str, ...] = (),
        constraints: tuple[str, ...] = (),
        metadata: Mapping[str, Any] | None = None,
    ) -> ActionCandidate:
        return ActionCandidate(
            action_type=action_type,
            priority=priority,
            rationale=rationale,
            requires_approval=self.DEFAULT_APPROVAL[action_type],
            required_evidence=required_evidence,
            constraints=constraints,
            metadata=metadata,
        )

    def _deduplicate(
        self,
        candidates: list[ActionCandidate],
    ) -> list[ActionCandidate]:
        seen: set[ActionType] = set()
        result: list[ActionCandidate] = []

        for candidate in sorted(
            candidates,
            key=lambda item: item.priority,
        ):
            if candidate.action_type in seen:
                continue

            seen.add(candidate.action_type)
            result.append(candidate)

        return result

    @staticmethod
    def _clamp(value: float | None) -> float:
        if value is None:
            return 0.0

        return max(0.0, min(1.0, float(value)))