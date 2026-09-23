"""
Evidence sufficiency assessment.

Determines whether the currently collected evidence is sufficient to
support a defensible investigation decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.app.schemas.evidence import Evidence, EvidenceSourceType
from backend.evidence.scorer import EvidenceScorer


@dataclass(slots=True)
class SufficiencyResult:
    """Result of an evidence sufficiency assessment."""

    sufficient: bool
    score: float
    missing_sources: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    evidence_count: int = 0


class EvidenceSufficiency:
    """Assess whether available evidence supports a defensible action."""

    MINIMUM_SCORE = 0.55
    HIGH_RISK_MINIMUM_SCORE = 0.70

    def __init__(
        self,
        *,
        scorer: EvidenceScorer | None = None,
    ) -> None:
        self.scorer = scorer or EvidenceScorer()

    def assess(
        self,
        evidence: list[Evidence],
        *,
        risk_score: float | None = None,
        required_sources: list[EvidenceSourceType] | None = None,
    ) -> SufficiencyResult:
        """
        Assess evidence sufficiency.

        High-risk investigations require stronger evidence than ordinary
        investigations. Explicitly requested source categories are also
        checked independently.
        """
        evidence = list(evidence or [])

        score = self.scorer.score_many(evidence)

        threshold = (
            self.HIGH_RISK_MINIMUM_SCORE
            if risk_score is not None and risk_score >= 0.65
            else self.MINIMUM_SCORE
        )

        available_sources = {
            item.source_type
            for item in evidence
            if getattr(item, "source_type", None) is not None
        }

        required = required_sources or []
        missing_sources = [
            source.value
            for source in required
            if source not in available_sources
        ]

        reasons: list[str] = []

        if not evidence:
            reasons.append("No evidence has been collected.")

        if score < threshold:
            reasons.append(
                f"Evidence score {score:.2f} is below the "
                f"required threshold {threshold:.2f}."
            )

        if missing_sources:
            reasons.append(
                "Required evidence source categories are missing: "
                + ", ".join(missing_sources)
                + "."
            )

        sufficient = (
            bool(evidence)
            and score >= threshold
            and not missing_sources
        )

        if sufficient:
            reasons.append(
                "Available evidence meets the configured sufficiency "
                "threshold."
            )

        return SufficiencyResult(
            sufficient=sufficient,
            score=round(score, 4),
            missing_sources=missing_sources,
            reasons=reasons,
            evidence_count=len(evidence),
        )

    def is_sufficient(
        self,
        evidence: list[Evidence],
        *,
        risk_score: float | None = None,
        required_sources: list[EvidenceSourceType] | None = None,
    ) -> bool:
        """Convenience method returning only the sufficiency decision."""
        return self.assess(
            evidence,
            risk_score=risk_score,
            required_sources=required_sources,
        ).sufficient

    @staticmethod
    def required_sources_for_risk(
        risk_score: float | None,
    ) -> list[EvidenceSourceType]:
        """
        Return source categories normally useful for a risk level.

        This does not fabricate evidence; it only identifies categories
        that may need to be collected.
        """
        if risk_score is None:
            return [
                EvidenceSourceType.TRANSACTION,
                EvidenceSourceType.GRAPH,
            ]

        if risk_score >= 0.85:
            return [
                EvidenceSourceType.TRANSACTION,
                EvidenceSourceType.GRAPH,
                EvidenceSourceType.HISTORICAL_CASE,
                EvidenceSourceType.CUSTOMER,
            ]

        if risk_score >= 0.65:
            return [
                EvidenceSourceType.TRANSACTION,
                EvidenceSourceType.GRAPH,
                EvidenceSourceType.HISTORICAL_CASE,
            ]

        return [
            EvidenceSourceType.TRANSACTION,
            EvidenceSourceType.GRAPH,
        ]