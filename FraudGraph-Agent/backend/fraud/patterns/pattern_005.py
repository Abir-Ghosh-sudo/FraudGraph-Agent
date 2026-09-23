"""
Fraud Pattern 005: Cross-Entity Connection.

Detects suspicious connections between transaction entities using
available account, customer, device, IP, and connection identifiers.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any


class CrossEntityConnectionPattern:
    """Detect suspicious relationships across transaction entities."""

    pattern_id = "cross_entity_connection"
    pattern_name = "Cross-Entity Connection"
    severity = "high"

    ENTITY_KEYS = (
        ("account_id", "AccountID"),
        ("customer_id", "CustomerID"),
        ("device_id", "DeviceID"),
        ("ip_address", "IP", "IpAddress", "ip"),
        ("connection_id", "ConnectionID"),
    )

    def detect(
        self,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        records = self._records(context)

        entity_accounts: dict[str, set[str]] = defaultdict(set)

        for record in records:
            account_id = self._value(
                record,
                "account_id",
                "AccountID",
                "customer_id",
                "CustomerID",
            )

            if account_id is None:
                continue

            account_id = str(account_id)

            for aliases in self.ENTITY_KEYS:
                value = self._value(record, *aliases)

                if value is None:
                    continue

                entity_key = f"{aliases[0]}:{value}"
                entity_accounts[entity_key].add(account_id)

        suspicious = {
            entity: sorted(accounts)
            for entity, accounts in entity_accounts.items()
            if len(accounts) > 1
        }

        if not suspicious:
            return {
                "pattern_id": self.pattern_id,
                "pattern_name": self.pattern_name,
                "detected": False,
                "confidence": 0.0,
                "severity": self.severity,
                "rationale": (
                    "No shared cross-entity connection involving "
                    "multiple accounts was detected."
                ),
                "evidence_ids": [],
                "metadata": {},
            }

        maximum_accounts = max(
            len(accounts)
            for accounts in suspicious.values()
        )

        confidence = min(
            1.0,
            0.60 + max(0, maximum_accounts - 2) * 0.10,
        )

        evidence_ids = self._evidence_ids(context)

        return {
            "pattern_id": self.pattern_id,
            "pattern_name": self.pattern_name,
            "detected": True,
            "confidence": confidence,
            "severity": self.severity,
            "rationale": (
                f"{len(suspicious)} shared connection(s) link "
                "multiple customer/account identities."
            ),
            "evidence_ids": evidence_ids,
            "metadata": {
                "shared_connections": suspicious,
                "shared_connection_count": len(suspicious),
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
    def _value(
        record: Mapping[str, Any],
        *keys: str,
    ) -> Any:
        for key in keys:
            value = record.get(key)

            if value is not None and value != "":
                return value

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
    return CrossEntityConnectionPattern().detect(context)