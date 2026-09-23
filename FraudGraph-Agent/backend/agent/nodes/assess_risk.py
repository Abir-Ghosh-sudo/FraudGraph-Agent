from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentDecision, AgentEventType, AgentStage
from backend.app.schemas.evidence import Evidence, EvidenceStrength, EvidenceType
from backend.app.schemas.investigation import (
    InvestigationAssessment,
    RiskLevel,
)
from backend.agent.state import AgentRuntimeState, advance_state

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
        "created_at": datetime.now(UTC),
    }


class AssessRiskNode:
    """
    Deterministic risk scorer.

    Combines evidence strength/confidence, detected pattern severity, and
    historical case outcomes into a single [0, 1] risk score.
    Maps score → RiskLevel via configurable thresholds.

    Never calls LLM — always deterministic so results are reproducible.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def __call__(self, state: AgentRuntimeState) -> AgentRuntimeState:
        evidence: list[Evidence] = list(state.get("evidence", []))
        patterns: list[dict[str, Any]] = list(state.get("detected_patterns", []))
        related_cases: list[dict[str, Any]] = list(state.get("related_cases", []))
        investigation_id = state.get("investigation_id", "")
        events = list(state.get("events", []))

        # ------------------------------------------------------------------ #
        # 1. Evidence contribution                                            #
        # ------------------------------------------------------------------ #
        evidence_score, confidence = self._score_evidence(evidence)

        # ------------------------------------------------------------------ #
        # 2. Pattern contribution                                             #
        # ------------------------------------------------------------------ #
        pattern_score = self._score_patterns(patterns)

        # ------------------------------------------------------------------ #
        # 3. Historical case contribution                                      #
        # ------------------------------------------------------------------ #
        history_score = self._score_history(related_cases)

        # ------------------------------------------------------------------ #
        # 4. Trigger risk prior                                               #
        # ------------------------------------------------------------------ #
        trigger = state.get("trigger", {})
        trigger_prior = trigger.get("risk_score") or 0.0
        if isinstance(trigger_prior, float):
            trigger_prior = max(0.0, min(1.0, trigger_prior))

        # ------------------------------------------------------------------ #
        # 5. Weighted combination                                              #
        # ------------------------------------------------------------------ #
        risk_score = (
            evidence_score * 0.40
            + pattern_score * 0.30
            + trigger_prior * 0.15
            + history_score * 0.15
        )

        risk_score = max(0.0, min(1.0, risk_score))

        # ------------------------------------------------------------------ #
        # 6. Uncertainty = 1 - confidence                                     #
        # ------------------------------------------------------------------ #
        uncertainty = max(0.0, min(1.0, 1.0 - confidence))

        # ------------------------------------------------------------------ #
        # 7. Risk level from thresholds                                        #
        # ------------------------------------------------------------------ #
        risk_level = self._score_to_level(risk_score)

        # ------------------------------------------------------------------ #
        # 8. Fraud type inference (heuristic from patterns/evidence)          #
        # ------------------------------------------------------------------ #
        fraud_type = self._infer_fraud_type(evidence, patterns)

        # ------------------------------------------------------------------ #
        # 9. Rationale                                                         #
        # ------------------------------------------------------------------ #
        rationale = self._build_rationale(
            evidence_score=evidence_score,
            pattern_score=pattern_score,
            trigger_prior=trigger_prior,
            history_score=history_score,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            evidence_count=len(evidence),
            pattern_count=len(patterns),
        )

        assessment = InvestigationAssessment(
            risk_score=round(risk_score, 4),
            risk_level=risk_level,
            uncertainty=round(uncertainty, 4),
            confidence=round(confidence, 4),
            fraud_type=fraud_type,
            rationale=rationale,
        )

        decision = AgentDecision(
            decision=f"Risk assessed: {risk_level} ({risk_score:.3f})",
            rationale=rationale,
            evidence_ids=[ev.evidence_id for ev in evidence],
            confidence=round(confidence, 4),
            created_at=datetime.now(UTC),
        )

        events.append(
            _make_event(
                state,
                AgentEventType.RISK_ASSESSED,
                f"Risk level: {risk_level} (score={risk_score:.3f}, confidence={confidence:.3f})",
                {
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "confidence": confidence,
                    "uncertainty": uncertainty,
                    "fraud_type": fraud_type,
                    "evidence_count": len(evidence),
                    "pattern_count": len(patterns),
                },
            )
        )

        logger.info(
            "risk assessment complete",
            investigation_id=investigation_id,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            uncertainty=uncertainty,
        )

        updated = advance_state(state, AgentStage.ASSESS_RISK)
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
        """Returns (evidence_score, confidence)."""
        if not evidence:
            return 0.0, 0.0

        total_contribution = 0.0
        total_confidence = 0.0
        total_reliability = 0.0

        for ev in evidence:
            weight = _STRENGTH_WEIGHT.get(ev.strength, 0.50)

            if ev.evidence_type == EvidenceType.CONTRADICTING:
                contribution = -weight * ev.confidence
            else:
                contribution = weight * ev.confidence

            total_contribution += contribution
            total_confidence += ev.confidence
            total_reliability += ev.reliability

        n = len(evidence)
        avg_score = max(0.0, min(1.0, total_contribution / n))
        avg_confidence = min(1.0, total_confidence / n)

        # More evidence → higher confidence (logarithmic growth)
        import math
        evidence_volume_bonus = min(0.20, math.log1p(n) * 0.05)
        final_confidence = min(1.0, avg_confidence + evidence_volume_bonus)

        return round(avg_score, 4), round(final_confidence, 4)

    @staticmethod
    def _score_patterns(patterns: list[dict[str, Any]]) -> float:
        if not patterns:
            return 0.0

        total = 0.0
        for p in patterns:
            severity = p.get("severity", "medium")
            weight = _PATTERN_SEVERITY_WEIGHT.get(severity, 0.10)
            confidence = float(p.get("confidence", 0.5))
            total += weight * confidence

        return min(1.0, total)

    @staticmethod
    def _score_history(related_cases: list[dict[str, Any]]) -> float:
        if not related_cases:
            return 0.0

        fraud_cases = [
            c for c in related_cases
            if c.get("outcome", "").lower() in ("fraud", "confirmed_fraud", "confirmed")
        ]

        if not fraud_cases:
            return 0.0

        fraud_ratio = len(fraud_cases) / len(related_cases)
        avg_similarity = sum(
            float(c.get("similarity", 0.5)) for c in fraud_cases
        ) / len(fraud_cases)

        return round(fraud_ratio * avg_similarity * 0.50, 4)

    def _score_to_level(self, score: float) -> RiskLevel:
        thresholds = self.settings.risk_thresholds

        if score < thresholds.get("low", 0.30):
            return RiskLevel.LOW
        if score < thresholds.get("medium", 0.60):
            return RiskLevel.MEDIUM
        if score < thresholds.get("high", 0.85):
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL

    @staticmethod
    def _infer_fraud_type(
        evidence: list[Evidence],
        patterns: list[dict[str, Any]],
    ) -> str | None:
        pattern_names = [p.get("name", "") for p in patterns]

        if "FRAUD_MARKER" in pattern_names:
            return "confirmed_fraud_marker"
        if "DEVICE_REUSE" in pattern_names and "IP_REUSE" in pattern_names:
            return "account_takeover"
        if "DEVICE_REUSE" in pattern_names:
            return "device_fraud"
        if "IP_REUSE" in pattern_names:
            return "coordinated_fraud"
        if "VELOCITY" in pattern_names:
            return "velocity_fraud"

        fraud_markers = [
            ev for ev in evidence
            if ev.evidence_type == EvidenceType.DIRECT
            and "fraud" in (ev.title or "").lower()
        ]
        if fraud_markers:
            return "unclassified_fraud"

        return None

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
        evidence_count: int,
        pattern_count: int,
    ) -> str:
        return (
            f"Risk score {risk_score:.3f} ({risk_level}) computed from: "
            f"evidence contribution={evidence_score:.3f} (n={evidence_count}), "
            f"pattern contribution={pattern_score:.3f} (n={pattern_count}), "
            f"trigger prior={trigger_prior:.3f}, "
            f"historical={history_score:.3f}. "
            f"Confidence={confidence:.3f}."
        )
