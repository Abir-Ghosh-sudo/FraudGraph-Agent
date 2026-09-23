"""
Fraud Pattern 004: Fraud Marker.

Detects explicit fraud-related markers already present in the
transaction or investigation evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class FraudMarkerPattern:
    """Detect explicit fraud indicators in available evidence."""

    pattern_id = "fraud_marker"
    pattern_name = "Fraud Marker"
    severity = "critical"

    FRAUD_KEYS = (
        "fraud_marker",
        "fraud_flag",
        "is_fraud",
        "fraud_indicator",
        "fraud_signal",
        "confirmed_fraud",
        "fraud_confirmed",
        "known_fraud",
    )

    def detect(
        self,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        records = self._records(context)

        markers: list[dict[str, Any]] = []

        for record in records:
            for key in self.FRAUD_KEYS:
                value = record.get(key)

                if self._is_positive(value):
                    markers.append(
                        {
                            "field": key,
                            "value": value,
                        }
                    )

        evidence_markers = self._evidence_markers(context)
        markers.extend(evidence_markers)

        if not markers:
            return {
                "pattern_id": self.pattern_id,
                "pattern_name": self.pattern_name,
                "detected": False,
                "confidence": 0.0,
                "severity": self.severity,
                "rationale": (
                    "No explicit fraud marker was found in the "
                    "available investigation context."
                ),
                "evidence_ids": [],
                "metadata": {},
            }

        # Explicit confirmed/known fraud markers carry stronger
        # confidence than generic fraud signals.
        confirmed = any(
            marker["field"]
            in {
                "confirmed_fraud",
                "fraud_confirmed",
                "known_fraud",
            }
            for marker in markers
        )

        confidence = 0.95 if confirmed else 0.85

        evidence_ids = self._evidence_ids(context)

        return {
            "pattern_id": self.pattern_id,
            "pattern_name": self.pattern_name,
            "detected": True,
            "confidence": confidence,
            "severity": self.severity,
            "rationale": (
                f"{len(markers)} explicit fraud marker(s) were "
                "identified in the available evidence."
            ),
            "evidence_ids": evidence_ids,
            "metadata": {
                "markers": markers,
                "confirmed_marker": confirmed,
            },
        }

    @staticmethod
    def _records(
        context: Mapping[str, Any],
    ) -> list[Mapping[str, Any]]:
        records = context.get("transactions")

        if records is None:
            records = context.get("records")

        if records is None:
            transaction = context.get("transaction")
            records = [transaction] if transaction else []

        if isinstance(records, Mapping):
            return [records]

        return [
            record
            for record in records or []
            if isinstance(record, Mapping)
        ]

    @staticmethod
    def _is_positive(value: Any) -> bool:
        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return value != 0

        if isinstance(value, str):
            normalized = value.strip().lower()

            return normalized in {
                "true",
                "yes",
                "y",
                "fraud",
                "confirmed",
                "positive",
                "high",
                "critical",
                "1",
            }

        return False

    @staticmethod
    def _evidence_markers(
        context: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        evidence = context.get("evidence", [])

        if isinstance(evidence, Mapping):
            evidence = [evidence]

        markers: list[dict[str, Any]] = []

        for item in evidence or []:
            if not isinstance(item, Mapping):
                continue

            for key in FraudMarkerPattern.FRAUD_KEYS:
                value = item.get(key)

                if FraudMarkerPattern._is_positive(value):
                    markers.append(
                        {
                            "field": key,
                            "value": value,
                        }
                    )

        return markers

    @staticmethod
    def _evidence_ids(
        context: Mapping[str, Any],
    ) -> list[str]:
        evidence = context.get("evidence", [])

        if isinstance(evidence, Mapping):
            evidence = [evidence]

        ids: list[str] = []

        for item in evidence or []:
            if isinstance(item, Mapping):
                value = item.get("evidence_id") or item.get("id")
            else:
                value = getattr(item, "evidence_id", None)

            if value:
                ids.append(str(value))

        return list(dict.fromkeys(ids))


def detect(context: Mapping[str, Any]) -> dict[str, Any]:
    """Functional entry point for the pattern."""
    return FraudMarkerPattern().detect(context)