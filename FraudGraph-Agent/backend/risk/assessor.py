"""
Reusable fraud-risk assessment service.

Combines model risk, fraud-pattern findings, evidence quality, and
historical signals into a normalized risk assessment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.evidence.scorer import EvidenceScorer


@dataclass(slots=True)
class RiskAssessment:
    """Normalized result of a fraud-risk assessment."""

    score: float
    level: str
    confidence: float
    rationale: str
    factors: list[dict[str, Any]] = field(default_factory=list)


class RiskAssessor:
    """Calculate deterministic investigation risk."""

    def __init__(
        self,
        *,
        evidence_scorer: EvidenceScorer | None = None,
    ) -> None:
        self.evidence_scorer = evidence_scorer or EvidenceScorer()

    def assess(
        self,
        *,
        model_score: float | None = None,
        pattern_findings: list[Any] | None = None,
        evidence: list[Any] | None = None,
        historical_risk: float | None = None,
        trigger_type: str | None = None,
    ) -> RiskAssessment:
        factors: list[dict[str, Any]] = []

        scores: list[float] = []

        if model_score is not None:
            value = self._clamp(model_score)
            scores.append(value)
            factors.append(
                {
                    "type": "model_score",
                    "value": round(value, 4),
                }
            )

        if historical_risk is not None:
            value = self._clamp(historical_risk)
            scores.append(value)
            factors.append(
                {
                    "type": "historical_risk",
                    "value": round(value, 4),
                }
            )

        findings = list(pattern_findings or [])

        detected_findings = [
            finding
            for finding in findings
            if self._detected(finding)
        ]

        if detected_findings:
            pattern_score = max(
                self._confidence(finding)
                for finding in detected_findings
            )

            scores.append(pattern_score)

            factors.append(
                {
                    "type": "fraud_patterns",
                    "value": round(pattern_score, 4),
                    "count": len(detected_findings),
                    "patterns": [
                        self._pattern_id(finding)
                        for finding in detected_findings
                    ],
                }
            )

        evidence_items = list(evidence or [])

        if evidence_items:
            evidence_score = self.evidence_scorer.score_many(
                evidence_items
            )

            factors.append(
                {
                    "type": "evidence_quality",
                    "value": round(evidence_score, 4),
                }
            )

        score = self._combine(
            scores=scores,
            pattern_count=len(detected_findings),
            evidence_count=len(evidence_items),
        )

        confidence = self._confidence_score(
            evidence_count=len(evidence_items),
            pattern_count=len(detected_findings),
            score=score,
        )

        level = self.level(score)

        rationale = self._rationale(
            score=score,
            level=level,
            factors=factors,
            trigger_type=trigger_type,
        )

        return RiskAssessment(
            score=round(score, 4),
            level=level,
            confidence=round(confidence, 4),
            rationale=rationale,
            factors=factors,
        )

    @staticmethod
    def level(score: float) -> str:
        """Map normalized risk score to a risk level."""
        value = max(0.0, min(1.0, float(score)))

        if value >= 0.85:
            return "critical"

        if value >= 0.65:
            return "high"

        if value >= 0.40:
            return "medium"

        return "low"

    @staticmethod
    def _combine(
        *,
        scores: list[float],
        pattern_count: int,
        evidence_count: int,
    ) -> float:
        if not scores:
            return 0.0

        # The strongest signal is the primary risk indicator.
        strongest = max(scores)

        # Multiple independent fraud signals increase risk, but with a
        # bounded contribution to avoid runaway scores.
        pattern_bonus = min(
            0.20,
            max(0, pattern_count - 1) * 0.05,
        )

        # Evidence affects confidence rather than directly creating fraud
        # risk, so only a small corroboration bonus is applied.
        evidence_bonus = min(
            0.10,
            evidence_count * 0.02,
        )

        return max(
            0.0,
            min(
                1.0,
                strongest + pattern_bonus + evidence_bonus,
            ),
        )

    @staticmethod
    def _confidence_score(
        *,
        evidence_count: int,
        pattern_count: int,
        score: float,
    ) -> float:
        confidence = 0.30

        if evidence_count:
            confidence += min(0.30, evidence_count * 0.06)

        if pattern_count:
            confidence += min(0.25, pattern_count * 0.08)

        if score >= 0.65:
            confidence += 0.10

        return max(0.0, min(1.0, confidence))

    @staticmethod
    def _rationale(
        *,
        score: float,
        level: str,
        factors: list[dict[str, Any]],
        trigger_type: str | None,
    ) -> str:
        factor_names = [
            str(factor["type"])
            for factor in factors
        ]

        reason = (
            "Risk assessment is based on "
            + (
                ", ".join(factor_names)
                if factor_names
                else "available investigation context"
            )
            + "."
        )

        if trigger_type:
            reason += f" Investigation trigger: {trigger_type}."

        return (
            f"Calculated risk score is {score:.2f}, classified as "
            f"{level}. {reason}"
        )

    @staticmethod
    def _detected(finding: Any) -> bool:
        if isinstance(finding, dict):
            return bool(
                finding.get(
                    "detected",
                    finding.get("match", False),
                )
            )

        return bool(getattr(finding, "detected", False))

    @staticmethod
    def _confidence(finding: Any) -> float:
        if isinstance(finding, dict):
            value = finding.get("confidence", 0.0)
        else:
            value = getattr(finding, "confidence", 0.0)

        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _pattern_id(finding: Any) -> str:
        if isinstance(finding, dict):
            return str(
                finding.get("pattern_id")
                or finding.get("pattern_name")
                or "unknown"
            )

        return str(
            getattr(finding, "pattern_id", None)
            or getattr(finding, "pattern_name", None)
            or "unknown"
        )

    @staticmethod
    def _clamp(value: float) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0