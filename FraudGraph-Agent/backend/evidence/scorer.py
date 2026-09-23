"""
Evidence quality and strength scoring.

Produces a deterministic 0.0-1.0 score from the evidence attributes
already defined by the project schema.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from backend.app.schemas.evidence import (
    Evidence,
    EvidenceStrength,
    EvidenceType,
)


class EvidenceScorer:
    """Score evidence quality without changing the evidence itself."""

    STRENGTH_SCORES = {
        EvidenceStrength.WEAK: 0.25,
        EvidenceStrength.MODERATE: 0.50,
        EvidenceStrength.STRONG: 0.75,
        EvidenceStrength.VERY_STRONG: 1.00,
    }

    TYPE_WEIGHTS = {
        EvidenceType.DIRECT: 1.00,
        EvidenceType.DERIVED: 0.80,
        EvidenceType.CORROBORATING: 0.75,
        EvidenceType.CONTRADICTING: 0.60,
        EvidenceType.CONTEXTUAL: 0.45,
    }

    def score(self, evidence: Evidence | Mapping[str, Any]) -> float:
        """Return a normalized quality score for one evidence item."""
        strength = self._value(evidence, "strength")
        evidence_type = self._value(evidence, "evidence_type")

        strength_score = self._strength_score(strength)
        type_weight = self._type_weight(evidence_type)

        score = strength_score * type_weight

        # Evidence with a description/data payload is more useful than
        # an otherwise empty evidence shell.
        description = self._value(evidence, "description")
        data = self._value(evidence, "data")

        if description:
            score += 0.05

        if isinstance(data, Mapping) and data:
            score += 0.05

        return self._clamp(score)

    def score_many(
        self,
        evidence: Sequence[Evidence | Mapping[str, Any]],
    ) -> float:
        """
        Return the aggregate evidence score.

        Uses the strongest available evidence while giving corroborating
        evidence a small additional contribution.
        """
        if not evidence:
            return 0.0

        individual_scores = [
            self.score(item)
            for item in evidence
        ]

        strongest = max(individual_scores)

        additional = sum(
            score * 0.15
            for score in sorted(
                individual_scores,
                reverse=True,
            )[1:4]
        )

        return self._clamp(strongest + additional)

    def classify(
        self,
        score: float,
    ) -> EvidenceStrength:
        """Convert a normalized score into an EvidenceStrength value."""
        value = self._clamp(score)

        if value >= 0.85:
            return EvidenceStrength.VERY_STRONG

        if value >= 0.65:
            return EvidenceStrength.STRONG

        if value >= 0.40:
            return EvidenceStrength.MODERATE

        return EvidenceStrength.WEAK

    def explain(
        self,
        evidence: Evidence | Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return score and contributing attributes."""
        score = self.score(evidence)

        return {
            "score": round(score, 4),
            "strength": self._value(evidence, "strength"),
            "evidence_type": self._value(evidence, "evidence_type"),
            "classified_strength": self.classify(score).value,
        }

    def _strength_score(self, value: Any) -> float:
        if isinstance(value, EvidenceStrength):
            return self.STRENGTH_SCORES.get(value, 0.0)

        if value is not None:
            normalized = str(value).strip().lower()

            for strength, score in self.STRENGTH_SCORES.items():
                if normalized in {
                    strength.value.lower(),
                    strength.name.lower(),
                }:
                    return score

        return 0.0

    def _type_weight(self, value: Any) -> float:
        if isinstance(value, EvidenceType):
            return self.TYPE_WEIGHTS.get(value, 0.0)

        if value is not None:
            normalized = str(value).strip().lower()

            for evidence_type, weight in self.TYPE_WEIGHTS.items():
                if normalized in {
                    evidence_type.value.lower(),
                    evidence_type.name.lower(),
                }:
                    return weight

        return 0.0

    @staticmethod
    def _value(
        evidence: Evidence | Mapping[str, Any],
        key: str,
    ) -> Any:
        if isinstance(evidence, Mapping):
            return evidence.get(key)

        return getattr(evidence, key, None)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))