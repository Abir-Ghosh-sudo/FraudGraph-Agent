"""
Agent-facing transaction tools.

Provides a small abstraction for retrieving transaction information needed
during fraud investigations. A concrete transaction service can be injected
by the application layer.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence


TransactionFetcher = Callable[..., Any]


class TransactionTools:
    """Interface for transaction retrieval available to the agent."""

    def __init__(
        self,
        fetcher: TransactionFetcher | None = None,
    ) -> None:
        self.fetcher = fetcher

    def get(
        self,
        transaction_id: str,
    ) -> Any:
        """Retrieve a transaction by its identifier."""
        if self.fetcher is None:
            raise RuntimeError(
                "No transaction fetcher has been configured."
            )

        return self.fetcher(transaction_id=transaction_id)

    def search(
        self,
        filters: Mapping[str, Any] | None = None,
        *,
        limit: int = 100,
    ) -> list[Any]:
        """Retrieve transactions matching investigation filters."""
        if self.fetcher is None:
            raise RuntimeError(
                "No transaction fetcher has been configured."
            )

        result = self.fetcher(
            filters=dict(filters or {}),
            limit=limit,
        )

        if result is None:
            return []

        if isinstance(result, Sequence) and not isinstance(
            result,
            (str, bytes, bytearray),
        ):
            return list(result)

        return [result]

    def by_account(
        self,
        account_id: str,
        *,
        limit: int = 100,
    ) -> list[Any]:
        """Retrieve recent transactions associated with an account."""
        return self.search(
            {"account_id": account_id},
            limit=limit,
        )

    def by_customer(
        self,
        customer_id: str,
        *,
        limit: int = 100,
    ) -> list[Any]:
        """Retrieve recent transactions associated with a customer."""
        return self.search(
            {"customer_id": customer_id},
            limit=limit,
        )

    def by_device(
        self,
        device_id: str,
        *,
        limit: int = 100,
    ) -> list[Any]:
        """Retrieve transactions associated with a device."""
        return self.search(
            {"device_id": device_id},
            limit=limit,
        )

    def by_ip(
        self,
        ip_address: str,
        *,
        limit: int = 100,
    ) -> list[Any]:
        """Retrieve transactions associated with an IP address."""
        return self.search(
            {"ip_address": ip_address},
            limit=limit,
        )


def create_transaction_tools(
    fetcher: TransactionFetcher | None = None,
) -> TransactionTools:
    """Create the default transaction-tool collection."""
    return TransactionTools(fetcher=fetcher)