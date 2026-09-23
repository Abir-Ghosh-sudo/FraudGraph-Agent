"""
Account-control integration boundary.

Provides safe account-level action handlers for the fraud investigation
agent. Real banking/account systems can be connected later through this
interface without changing agent orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(slots=True)
class AccountActionResult:
    """Result of an account-control operation."""

    account_id: str
    action: str
    status: str
    message: str
    provider_reference: str | None = None
    executed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.executed_at is None:
            self.executed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "account_id": self.account_id,
            "action": self.action,
            "status": self.status,
            "message": self.message,
            "provider_reference": self.provider_reference,
            "executed_at": self.executed_at.isoformat(),
        }


class AccountControl:
    """
    Account-control abstraction.

    ``dry_run=True`` is the safe default and performs no real account
    modification.
    """

    def __init__(self, *, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    @staticmethod
    def _account_id(payload: Mapping[str, Any]) -> str:
        value = payload.get("account_id") or payload.get("id")

        if value is None or not str(value).strip():
            raise ValueError("account_id is required.")

        return str(value)

    def monitor_account(
        self,
        payload: Mapping[str, Any],
    ) -> AccountActionResult:
        """Place an account under enhanced monitoring."""
        account_id = self._account_id(payload)

        if self.dry_run:
            return AccountActionResult(
                account_id=account_id,
                action="monitor_account",
                status="simulated",
                message=(
                    f"Account '{account_id}' would be placed under "
                    "enhanced monitoring."
                ),
                provider_reference=f"SIM-MONITOR-{account_id}",
            )

        return AccountActionResult(
            account_id=account_id,
            action="monitor_account",
            status="accepted",
            message=f"Account '{account_id}' was placed under monitoring.",
        )

    def block_account(
        self,
        payload: Mapping[str, Any],
    ) -> AccountActionResult:
        """Block an account."""
        account_id = self._account_id(payload)

        if self.dry_run:
            return AccountActionResult(
                account_id=account_id,
                action="block_account",
                status="simulated",
                message=(
                    f"Account '{account_id}' would be blocked in a "
                    "live account-control system."
                ),
                provider_reference=f"SIM-BLOCK-{account_id}",
            )

        return AccountActionResult(
            account_id=account_id,
            action="block_account",
            status="accepted",
            message=f"Account '{account_id}' was blocked.",
        )

    def handler(self, action: str):
        """Return an executor-compatible handler."""
        handlers = {
            "monitor_account": self.monitor_account,
            "block_account": self.block_account,
        }

        try:
            return handlers[action]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported account-control action: {action}"
            ) from exc