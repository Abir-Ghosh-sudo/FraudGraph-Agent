"""
Fraud scoring utilities.

Converts normalized fraud findings and investigation signals into a
bounded 0.0-1.0 fraud risk score.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


DEFAULT_PATTERN_WEIGHTS: dict[str, float] = {
    "device_reuse": 0.20,
    "ip_reuse": 0.15,
    "velocity": 0.20,
    "fraud_marker": 0.30,
}


class FraudScorer:
    """Calculate a deterministic fraud score from investigation signals."""

    def __init__(
        self,
        *,
        pattern_weights: Mapping[str, float] | None = None,
    ) -> None:
        self.pattern_weights = {
            key.lower(): max(0.0, float(value))
            for key, value in (
                pattern_weights or DEFAULT_PATTERN_WEIGHTS
            ).items()
        }

    def score(
        self,
        findings: Sequence[Any] | None = None,
        *,
        transaction: Mapping[str, Any] | None = None,
        historical_risk: float | None = None,
        base_score: float | None = None,
    ) -> float:
        """
        Return a fraud score between 0.0 and 1.0.

        Existing bank/model risk is preserved as an input signal, while
        detected fraud patterns contribute additional evidence.
        """
        finding_list = list(findings or [])

        score = self._normalize_score(base_score)

        if historical_risk is not None:
            historical = self._normalize_score(historical_risk)
            score = max(score, historical)

        for finding in finding_list:
            if not self._is_detected(finding):
                continue

            confidence = self._confidence(finding)
            pattern_id = self._pattern_id(finding)

            weight = self.pattern_weights.get(
                pattern_id.lower(),
                0.10,
            )

            score += weight * confidence

        if transaction:
            score += self._transaction_signal(transaction)

        return self._clamp(score)

    def score_findings(self, findings: Sequence[Any]) -> float:
        """Convenience wrapper for scoring findings only."""
        return self.score(findings)

    def risk_level(self, score: float) -> str:
        """Convert a normalized score into a risk level."""
        value = self._clamp(score)

        if value >= 0.85:
            return "critical"

        if value >= 0.65:
            return "high"

        if value >= 0.40:
            return "medium"

        return "low"

    def explain(
        self,
        findings: Sequence[Any] | None = None,
        *,
        transaction: Mapping[str, Any] | None = None,
        historical_risk: float | None = None,
        base_score: float | None = None,
    ) -> dict[str, Any]:
        """Return score, risk level, and contributing signals."""
        finding_list = list(findings or [])

        score = self.score(
            finding_list,
            transaction=transaction,
            historical_risk=historical_risk,
            base_score=base_score,
        )

        contributors: list[dict[str, Any]] = []

        for finding in finding_list:
            if not self._is_detected(finding):
                continue

            pattern_id = self._pattern_id(finding)
            confidence = self._confidence(finding)
            weight = self.pattern_weights.get(
                pattern_id.lower(),
                0.10,
            )

            contributors.append(
                {
                    "pattern_id": pattern_id,
                    "confidence": confidence,
                    "weight": weight,
                    "contribution": round(
                        weight * confidence,
                        4,
                    ),
                }
            )

        return {
            "score": round(score, 4),
            "risk_level": self.risk_level(score),
            "contributors": contributors,
        }

    @staticmethod
    def _is_detected(finding: Any) -> bool:
        if isinstance(finding, Mapping):
            return bool(
                finding.get(
                    "detected",
                    finding.get(
                        "match",
                        finding.get("is_fraud", False),
                    ),
                )
            )

        return bool(getattr(finding, "detected", False))

    @staticmethod
    def _confidence(finding: Any) -> float:
        if isinstance(finding, Mapping):
            value = finding.get("confidence", 0.0)
        else:
            value = getattr(finding, "confidence", 0.0)

        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _pattern_id(finding: Any) -> str:
        if isinstance(finding, Mapping):
            value = (
                finding.get("pattern_id")
                or finding.get("pattern_name")
                or "unknown"
            )
        else:
            value = (
                getattr(finding, "pattern_id", None)
                or getattr(finding, "pattern_name", None)
                or "unknown"
            )

        return str(value)

    @staticmethod
    def _transaction_signal(
        transaction: Mapping[str, Any],
    ) -> float:
        """
        Extract small deterministic signals from transaction context.

        The existing bank/model risk field is handled separately, so this
        only considers explicit high-risk indicators when available.
        """
        bonus = 0.0

        for key in (
            "high_risk",
            "velocity_alert",
            "device_alert",
            "connection_alert",
        ):
            if transaction.get(key) is True:
                bonus += 0.05

        return min(bonus, 0.20)

    @staticmethod
    def _normalize_score(value: float | None) -> float:
        if value is None:
            return 0.0

        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))