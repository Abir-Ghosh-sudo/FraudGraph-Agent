from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentDecision, AgentEventType, AgentStage
from backend.app.schemas.evidence import Evidence, EvidenceStrength, EvidenceType
from backend.app.schemas.investigation import (
    InvestigationAssessment,
    RiskLevel,
)

logger = get_logger(__name__)


_STRENGTH_WEIGHT: dict[EvidenceStrength, float] = {
    EvidenceStrength.VERY_STRONG: 1.00,
    EvidenceStrength.STRONG: 0.75,
    EvidenceStrength.MODERATE: 0.50,
    EvidenceStrength.WEAK: 0.25,
}


_PATTERN_SEVERITY_WEIGHT: dict[str, float] = {
    "critical": 0.30,
    "high": 0.20,
    "medium": 0.12,
    "low": 0.05,
}


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _make_event(
    state: AgentRuntimeState,
    event_type: AgentEventType,
    message: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "event_id": f"evt_{uuid4().hex[:8]}",
        "event_type": event_type,
        "investigation_id": state.get("investigation_id", ""),
        "case_id": state.get("case_id"),
        "stage": AgentStage.ASSESS_RISK,
        "message": message,
        "payload": payload or {},
        "created_at": _utc_now(),
    }


class AssessRiskNode:
    """
    Deterministic risk assessment node.

    The score combines:

    - evidence strength and confidence
    - detected fraud-pattern severity
    - initial trigger risk score
    - historical related-case outcomes

    The result is always bounded to [0, 1] and mapped to the
    configured LOW / MEDIUM / HIGH / CRITICAL thresholds.

    No LLM is called from this node. This keeps the core risk
    calculation deterministic and reproducible.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(
        self,
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        """Workflow-compatible entry point."""
        return self.__call__(state)

    def __call__(
        self,
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        evidence = list(state.get("evidence", []))
        patterns = list(state.get("detected_patterns", []))
        related_cases = list(state.get("related_cases", []))
        events = list(state.get("events", []))

        investigation_id = state.get(
            "investigation_id",
            "",
        )

        # --------------------------------------------------------------
        # 1. Evidence contribution
        # --------------------------------------------------------------
        evidence_score, evidence_confidence = self._score_evidence(
            evidence
        )

        # --------------------------------------------------------------
        # 2. Pattern contribution
        # --------------------------------------------------------------
        pattern_score = self._score_patterns(
            patterns
        )

        # --------------------------------------------------------------
        # 3. Historical-case contribution
        # --------------------------------------------------------------
        history_score = self._score_history(
            related_cases
        )

        # --------------------------------------------------------------
        # 4. Trigger risk prior
        # --------------------------------------------------------------
        trigger = state.get(
            "trigger",
            {},
        )

        trigger_prior = self._safe_score(
            trigger.get("risk_score")
        )

        # --------------------------------------------------------------
        # 5. Weighted risk calculation
        # --------------------------------------------------------------
        risk_score = (
            evidence_score * 0.40
            + pattern_score * 0.30
            + trigger_prior * 0.15
            + history_score * 0.15
        )

        risk_score = self._clamp(
            risk_score
        )

        # --------------------------------------------------------------
        # 6. Confidence and uncertainty
        # --------------------------------------------------------------
        confidence = self._calculate_confidence(
            evidence_confidence=evidence_confidence,
            evidence_count=len(evidence),
            pattern_count=len(patterns),
            related_case_count=len(related_cases),
        )

        uncertainty = self._clamp(
            1.0 - confidence
        )

        # --------------------------------------------------------------
        # 7. Risk level
        # --------------------------------------------------------------
        risk_level = self._score_to_level(
            risk_score
        )

        # --------------------------------------------------------------
        # 8. Fraud-type inference
        # --------------------------------------------------------------
        fraud_type = self._infer_fraud_type(
            evidence,
            patterns,
        )

        # --------------------------------------------------------------
        # 9. Human-readable rationale
        # --------------------------------------------------------------
        rationale = self._build_rationale(
            evidence_score=evidence_score,
            pattern_score=pattern_score,
            trigger_prior=trigger_prior,
            history_score=history_score,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            uncertainty=uncertainty,
            evidence_count=len(evidence),
            pattern_count=len(patterns),
            related_case_count=len(related_cases),
        )

        assessment = InvestigationAssessment(
            risk_score=round(
                risk_score,
                4,
            ),
            risk_level=risk_level,
            uncertainty=round(
                uncertainty,
                4,
            ),
            confidence=round(
                confidence,
                4,
            ),
            fraud_type=fraud_type,
            rationale=rationale,
        )

        decision = AgentDecision(
            decision=(
                f"Risk assessed: "
                f"{risk_level.value} "
                f"({risk_score:.3f})"
            ),
            rationale=rationale,
            evidence_ids=[
                ev.evidence_id
                for ev in evidence
            ],
            confidence=round(
                confidence,
                4,
            ),
            created_at=_utc_now(),
        )

        # --------------------------------------------------------------
        # 10. Agent event
        # --------------------------------------------------------------
        events.append(
            _make_event(
                state,
                AgentEventType.RISK_ASSESSED,
                (
                    f"Risk level: {risk_level.value} "
                    f"(score={risk_score:.3f}, "
                    f"confidence={confidence:.3f})"
                ),
                {
                    "risk_score": risk_score,
                    "risk_level": risk_level.value,
                    "confidence": confidence,
                    "uncertainty": uncertainty,
                    "fraud_type": fraud_type,
                    "evidence_count": len(evidence),
                    "pattern_count": len(patterns),
                    "related_case_count": len(related_cases),
                },
            )
        )

        logger.info(
            "risk assessment complete",
            investigation_id=investigation_id,
            risk_score=risk_score,
            risk_level=risk_level.value,
            confidence=confidence,
            uncertainty=uncertainty,
        )

        # --------------------------------------------------------------
        # 11. Persist into runtime state
        # --------------------------------------------------------------
        updated = advance_state(
            state,
            AgentStage.ASSESS_RISK,
        )

        updated["assessment"] = assessment

        updated["decisions"] = [
            *state.get("decisions", []),
            decision,
        ]

        updated["events"] = events

        return updated

    def _score_evidence(
        self,
        evidence: list[Evidence],
    ) -> tuple[float, float]:
        """
        Calculate evidence contribution and evidence confidence.

        Contradicting evidence reduces the contribution but does not
        artificially remove the evidence from the confidence calculation.
        """
        if not evidence:
            return 0.0, 0.0

        total_contribution = 0.0
        total_confidence = 0.0

        for ev in evidence:
            strength_weight = _STRENGTH_WEIGHT.get(
                ev.strength,
                0.50,
            )

            confidence = self._clamp(
                float(ev.confidence)
            )

            if ev.evidence_type == EvidenceType.CONTRADICTING:
                contribution = (
                    -strength_weight
                    * confidence
                )
            else:
                contribution = (
                    strength_weight
                    * confidence
                )

            total_contribution += contribution
            total_confidence += confidence

        evidence_count = len(evidence)

        average_contribution = (
            total_contribution
            / evidence_count
        )

        average_confidence = (
            total_confidence
            / evidence_count
        )

        evidence_score = self._clamp(
            average_contribution
        )

        # Evidence volume increases confidence gradually rather than
        # linearly, preventing large evidence sets from immediately
        # producing artificial certainty.
        volume_bonus = min(
            0.20,
            math.log1p(evidence_count) * 0.05,
        )

        final_confidence = min(
            1.0,
            average_confidence + volume_bonus,
        )

        return (
            round(evidence_score, 4),
            round(final_confidence, 4),
        )

    @staticmethod
    def _score_patterns(
        patterns: list[dict[str, Any]],
    ) -> float:
        if not patterns:
            return 0.0

        total = 0.0

        for pattern in patterns:
            severity = str(
                pattern.get(
                    "severity",
                    "medium",
                )
            ).lower()

            severity_weight = _PATTERN_SEVERITY_WEIGHT.get(
                severity,
                0.10,
            )

            confidence = AssessRiskNode._safe_score(
                pattern.get("confidence"),
                default=0.5,
            )

            total += (
                severity_weight
                * confidence
            )

        return round(
            min(1.0, total),
            4,
        )

    @staticmethod
    def _score_history(
        related_cases: list[dict[str, Any]],
    ) -> float:
        if not related_cases:
            return 0.0

        fraud_outcomes = {
            "fraud",
            "confirmed_fraud",
            "confirmed",
        }

        fraud_cases = [
            case
            for case in related_cases
            if str(
                case.get(
                    "outcome",
                    "",
                )
            ).lower()
            in fraud_outcomes
        ]

        if not fraud_cases:
            return 0.0

        fraud_ratio = (
            len(fraud_cases)
            / len(related_cases)
        )

        similarities = [
            AssessRiskNode._safe_score(
                case.get("similarity"),
                default=0.5,
            )
            for case in fraud_cases
        ]

        average_similarity = (
            sum(similarities)
            / len(similarities)
        )

        # Historical cases are corroborating evidence, not the sole
        # determinant of risk.
        return round(
            min(
                1.0,
                fraud_ratio
                * average_similarity
                * 0.50,
            ),
            4,
        )

    def _score_to_level(
        self,
        score: float,
    ) -> RiskLevel:
        """
        Map the normalized risk score to configured thresholds.

        Settings uses individual threshold fields rather than a
        risk_thresholds dictionary.
        """
        if score < self.settings.risk_low_threshold:
            return RiskLevel.LOW

        if score < self.settings.risk_medium_threshold:
            return RiskLevel.MEDIUM

        if score < self.settings.risk_high_threshold:
            return RiskLevel.HIGH

        return RiskLevel.CRITICAL

    @staticmethod
    def _infer_fraud_type(
        evidence: list[Evidence],
        patterns: list[dict[str, Any]],
    ) -> str | None:
        pattern_names = {
            str(
                pattern.get(
                    "name",
                    "",
                )
            ).upper()
            for pattern in patterns
        }

        if "FRAUD_MARKER" in pattern_names:
            return "confirmed_fraud_marker"

        if {
            "DEVICE_REUSE",
            "IP_REUSE",
        }.issubset(pattern_names):
            return "account_takeover"

        if "DEVICE_REUSE" in pattern_names:
            return "device_fraud"

        if "IP_REUSE" in pattern_names:
            return "coordinated_fraud"

        if "VELOCITY" in pattern_names:
            return "velocity_fraud"

        direct_fraud_evidence = [
            ev
            for ev in evidence
            if (
                ev.evidence_type
                == EvidenceType.DIRECT
                and "fraud"
                in (ev.title or "").lower()
            )
        ]

        if direct_fraud_evidence:
            return "unclassified_fraud"

        return None

    @staticmethod
    def _calculate_confidence(
        *,
        evidence_confidence: float,
        evidence_count: int,
        pattern_count: int,
        related_case_count: int,
    ) -> float:
        """
        Combine confidence signals without allowing evidence volume
        alone to create high certainty.
        """
        confidence = evidence_confidence

        if pattern_count > 0:
            confidence += min(
                0.15,
                pattern_count * 0.05,
            )

        if related_case_count > 0:
            confidence += min(
                0.10,
                related_case_count * 0.02,
            )

        if evidence_count == 0:
            return 0.0

        return round(
            min(1.0, confidence),
            4,
        )

    @staticmethod
    def _build_rationale(
        *,
        evidence_score: float,
        pattern_score: float,
        trigger_prior: float,
        history_score: float,
        risk_score: float,
        risk_level: RiskLevel,
        confidence: float,
        uncertainty: float,
        evidence_count: int,
        pattern_count: int,
        related_case_count: int,
    ) -> str:
        return (
            f"Risk score {risk_score:.3f} "
            f"({risk_level.value}) was computed from "
            f"{evidence_count} evidence item(s), "
            f"{pattern_count} detected pattern(s), "
            f"{related_case_count} related historical case(s), "
            f"and an initial trigger risk prior of "
            f"{trigger_prior:.3f}. "
            f"Evidence contribution={evidence_score:.3f}; "
            f"pattern contribution={pattern_score:.3f}; "
            f"historical contribution={history_score:.3f}. "
            f"Confidence={confidence:.3f}; "
            f"uncertainty={uncertainty:.3f}."
        )

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        return max(
            0.0,
            min(1.0, value),
        )

    @staticmethod
    def _safe_score(
        value: Any,
        *,
        default: float = 0.0,
    ) -> float:
        if value is None:
            return default

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return default

        if not math.isfinite(numeric):
            return default

        return max(
            0.0,
            min(1.0, numeric),
        )