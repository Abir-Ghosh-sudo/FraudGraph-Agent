from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskThresholds:
    """Configurable thresholds used to classify fraud risk."""

    critical: float = 0.85
    high: float = 0.65
    medium: float = 0.40
    low: float = 0.0

    def __post_init__(self) -> None:
        values = (
            self.critical,
            self.high,
            self.medium,
            self.low,
        )

        if any(value < 0.0 or value > 1.0 for value in values):
            raise ValueError("Risk thresholds must be between 0.0 and 1.0.")

        if not (
            self.critical
            > self.high
            > self.medium
            > self.low
        ):
            raise ValueError(
                "Risk thresholds must be ordered as "
                "critical > high > medium > low."
            )

    def classify(self, score: float) -> str:
        """Classify a normalized risk score."""
        value = self.clamp(score)

        if value >= self.critical:
            return "critical"

        if value >= self.high:
            return "high"

        if value >= self.medium:
            return "medium"

        return "low"

    def clamp(self, score: float) -> float:
        """Clamp a risk score to the [0, 1] range."""
        return max(0.0, min(1.0, float(score)))

    def requires_immediate_attention(self, score: float) -> bool:
        """Return whether a score reaches the high-risk threshold."""
        return self.clamp(score) >= self.high

    def requires_critical_handling(self, score: float) -> bool:
        """Return whether a score reaches the critical threshold."""
        return self.clamp(score) >= self.critical