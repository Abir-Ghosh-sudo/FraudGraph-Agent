"""
Fraud Pattern 003: Transaction Velocity.

Detects unusually high transaction activity for the same account,
customer, device, or other available entity within a short period.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from datetime import datetime
from typing import Any


class VelocityPattern:
    """Detect suspicious transaction velocity."""

    pattern_id = "velocity"
    pattern_name = "Transaction Velocity"
    severity = "high"

    DEFAULT_WINDOW_SECONDS = 300
    DEFAULT_TRANSACTION_THRESHOLD = 5

    def __init__(
        self,
        *,
        window_seconds: int = DEFAULT_WINDOW_SECONDS,
        transaction_threshold: int = DEFAULT_TRANSACTION_THRESHOLD,
    ) -> None:
        self.window_seconds = max(1, int(window_seconds))
        self.transaction_threshold = max(2, int(transaction_threshold))

    def detect(
        self,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        records = self._records(context)

        grouped: dict[str, list[datetime]] = defaultdict(list)

        for record in records:
            entity_id = self._entity_id(record)

            if entity_id is None:
                continue

            timestamp = self._timestamp(record)

            if timestamp is not None:
                grouped[entity_id].append(timestamp)

        suspicious: dict[str, int] = {}

        for entity_id, timestamps in grouped.items():
            timestamps.sort()

            maximum_count = self._maximum_window_count(timestamps)

            if maximum_count >= self.transaction_threshold:
                suspicious[entity_id] = maximum_count

        if not suspicious:
            return {
                "pattern_id": self.pattern_id,
                "pattern_name": self.pattern_name,
                "detected": False,
                "confidence": 0.0,
                "severity": self.severity,
                "rationale": (
                    "No entity exceeded the configured transaction "
                    "velocity threshold."
                ),
                "evidence_ids": [],
                "metadata": {},
            }

        maximum_velocity = max(suspicious.values())

        confidence = min(
            1.0,
            0.55
            + max(
                0,
                maximum_velocity - self.transaction_threshold,
            )
            * 0.08,
        )

        evidence_ids = self._evidence_ids(context)

        return {
            "pattern_id": self.pattern_id,
            "pattern_name": self.pattern_name,
            "detected": True,
            "confidence": confidence,
            "severity": self.severity,
            "rationale": (
                f"{len(suspicious)} entity/entities exceeded the "
                f"velocity threshold of {self.transaction_threshold} "
                f"transactions within {self.window_seconds} seconds."
            ),
            "evidence_ids": evidence_ids,
            "metadata": {
                "window_seconds": self.window_seconds,
                "transaction_threshold": self.transaction_threshold,
                "suspicious_entities": suspicious,
                "maximum_velocity": maximum_velocity,
            },
        }

    def _maximum_window_count(
        self,
        timestamps: list[datetime],
    ) -> int:
        """Return the maximum number of events inside the time window."""
        if not timestamps:
            return 0

        left = 0
        maximum = 0

        for right, current in enumerate(timestamps):
            while (
                current - timestamps[left]
            ).total_seconds() > self.window_seconds:
                left += 1

            maximum = max(maximum, right - left + 1)

        return maximum

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
    def _entity_id(
        record: Mapping[str, Any],
    ) -> str | None:
        for key in (
            "account_id",
            "AccountID",
            "customer_id",
            "CustomerID",
            "device_id",
            "DeviceID",
        ):
            value = record.get(key)

            if value is not None and value != "":
                return str(value)

        return None

    @staticmethod
    def _timestamp(
        record: Mapping[str, Any],
    ) -> datetime | None:
        value = None

        for key in (
            "timestamp",
            "transaction_time",
            "transaction_datetime",
            "TransactionDT",
            "created_at",
            "createdAt",
        ):
            if record.get(key) is not None:
                value = record[key]
                break

        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(value)
            except (OverflowError, OSError, ValueError):
                return None

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )
            except ValueError:
                return None

        return None

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
    return VelocityPattern().detect(context)