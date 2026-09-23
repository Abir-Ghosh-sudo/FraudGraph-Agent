"""
Fraud Pattern 002: IP Reuse.

Detects cases where the same IP address is associated with multiple
customer/account identities.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any


class IPReusePattern:
    """Detect suspicious reuse of an IP address across identities."""

    pattern_id = "ip_reuse"
    pattern_name = "IP Reuse"
    severity = "medium"

    def detect(
        self,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        records = self._records(context)

        ip_accounts: dict[str, set[str]] = defaultdict(set)

        for record in records:
            ip_address = self._value(
                record,
                "ip_address",
                "IP",
                "IpAddress",
                "ip",
                "client_ip",
            )
            account_id = self._value(
                record,
                "account_id",
                "AccountID",
                "customer_id",
                "CustomerID",
            )

            if ip_address is None or account_id is None:
                continue

            ip_accounts[str(ip_address)].add(str(account_id))

        suspicious = {
            ip_address: sorted(accounts)
            for ip_address, accounts in ip_accounts.items()
            if len(accounts) > 1
        }

        if not suspicious:
            return {
                "pattern_id": self.pattern_id,
                "pattern_name": self.pattern_name,
                "detected": False,
                "confidence": 0.0,
                "severity": self.severity,
                "rationale": "No IP address was linked to multiple accounts.",
                "evidence_ids": [],
                "metadata": {},
            }

        max_accounts = max(
            len(accounts)
            for accounts in suspicious.values()
        )

        confidence = min(
            1.0,
            0.50 + max(0, max_accounts - 2) * 0.10,
        )

        evidence_ids = self._evidence_ids(context)

        return {
            "pattern_id": self.pattern_id,
            "pattern_name": self.pattern_name,
            "detected": True,
            "confidence": confidence,
            "severity": self.severity,
            "rationale": (
                f"{len(suspicious)} IP address(es) are associated "
                "with multiple customer/account identities."
            ),
            "evidence_ids": evidence_ids,
            "metadata": {
                "shared_ips": suspicious,
                "shared_ip_count": len(suspicious),
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
    return IPReusePattern().detect(context)