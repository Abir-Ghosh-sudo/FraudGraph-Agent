from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class ConfidenceAssessment:
    """Confidence assessment for an investigation conclusion."""

    confidence: float
    level: str
    factors: tuple[str, ...]
    rationale: str


class ConfidenceAssessor:
    """Calculate confidence from evidence, patterns, and risk signals."""

    LEVELS = (
        (0.85, "very_high"),
        (0.70, "high"),
        (0.50, "moderate"),
        (0.30, "low"),
        (0.00, "very_low"),
    )

    def assess(
        self,
        *,
        evidence: Iterable[Any] | None = None,
        patterns: Iterable[Any] | None = None,
        risk_score: float | None = None,
        model_confidence: float | None = None,
        uncertainty: float | None = None,
        historical_support: float | None = None,
    ) -> ConfidenceAssessment:
        evidence_items = list(evidence or [])
        pattern_items = list(patterns or [])

        factors: list[str] = []
        components: list[float] = []
        weights: list[float] = []

        evidence_score = self._evidence_confidence(evidence_items)
        if evidence_items:
            components.append(evidence_score)
            weights.append(0.35)
            factors.append(
                f"{len(evidence_items)} evidence item(s) available"
            )

        pattern_score = self._pattern_confidence(pattern_items)
        if pattern_items:
            components.append(pattern_score)
            weights.append(0.25)
            factors.append(
                f"{len(pattern_items)} fraud pattern(s) detected"
            )

        if risk_score is not None:
            risk = self._clamp(risk_score)
            components.append(risk)
            weights.append(0.15)
            factors.append(f"risk score={risk:.2f}")

        if model_confidence is not None:
            model = self._clamp(model_confidence)
            components.append(model)
            weights.append(0.15)
            factors.append(f"model confidence={model:.2f}")

        if historical_support is not None:
            historical = self._clamp(historical_support)
            components.append(historical)
            weights.append(0.10)
            factors.append(f"historical support={historical:.2f}")

        if not components:
            confidence = 0.0
        else:
            confidence = sum(
                component * weight
                for component, weight in zip(components, weights)
            ) / sum(weights)

        if uncertainty is not None:
            confidence *= 1.0 - self._clamp(uncertainty)
            if uncertainty > 0:
                factors.append(
                    f"uncertainty={self._clamp(uncertainty):.2f}"
                )

        confidence = self._clamp(confidence)
        level = self.level(confidence)

        rationale = self._rationale(
            confidence=confidence,
            level=level,
            evidence_count=len(evidence_items),
            pattern_count=len(pattern_items),
            uncertainty=uncertainty,
        )

        return ConfidenceAssessment(
            confidence=confidence,
            level=level,
            factors=tuple(factors),
            rationale=rationale,
        )

    def level(self, confidence: float) -> str:
        """Return a normalized confidence level."""
        value = self._clamp(confidence)

        for threshold, level in self.LEVELS:
            if value >= threshold:
                return level

        return "very_low"

    def _evidence_confidence(self, evidence: list[Any]) -> float:
        if not evidence:
            return 0.0

        scores: list[float] = []

        for item in evidence:
            if isinstance(item, Mapping):
                value = item.get("confidence")
                if value is None:
                    value = item.get("strength")
            else:
                value = getattr(item, "confidence", None)
                if value is None:
                    value = getattr(item, "strength", None)

            scores.append(self._normalize_value(value))

        return sum(scores) / len(scores)

    def _pattern_confidence(self, patterns: list[Any]) -> float:
        if not patterns:
            return 0.0

        scores: list[float] = []

        for pattern in patterns:
            if isinstance(pattern, Mapping):
                value = pattern.get("confidence")
                if value is None:
                    value = pattern.get("score")
            else:
                value = getattr(pattern, "confidence", None)
                if value is None:
                    value = getattr(pattern, "score", None)

            scores.append(self._normalize_value(value))

        return sum(scores) / len(scores)

    def _normalize_value(self, value: Any) -> float:
        if value is None:
            return 0.5

        if isinstance(value, str):
            normalized = value.strip().lower()

            mapping = {
                "very_low": 0.10,
                "low": 0.30,
                "moderate": 0.50,
                "medium": 0.50,
                "high": 0.75,
                "very_high": 0.95,
                "weak": 0.25,
                "strong": 0.75,
                "very_strong": 0.95,
            }

            if normalized in mapping:
                return mapping[normalized]

            try:
                value = float(value)
            except ValueError:
                return 0.5

        try:
            return self._clamp(float(value))
        except (TypeError, ValueError):
            return 0.5

    def _rationale(
        self,
        *,
        confidence: float,
        level: str,
        evidence_count: int,
        pattern_count: int,
        uncertainty: float | None,
    ) -> str:
        parts = [
            f"Conclusion confidence is {confidence:.2f} ({level}).",
            f"{evidence_count} evidence item(s) and "
            f"{pattern_count} pattern(s) contributed.",
        ]

        if uncertainty is not None:
            parts.append(
                f"Uncertainty adjustment applied: "
                f"{self._clamp(uncertainty):.2f}."
            )

        return " ".join(parts)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))