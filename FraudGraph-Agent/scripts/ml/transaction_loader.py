from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class TransactionRecordLoader:
    """Load transaction records and merge matching identity data."""

    IDENTITY_COLUMNS = [
        "TransactionID",
        *[f"id_{i:02d}" for i in range(1, 39)],
        "DeviceType",
        "DeviceInfo",
    ]

    def __init__(
        self,
        *,
        transactions_path: str | Path,
        identity_path: str | Path,
        chunk_size: int = 50_000,
    ) -> None:
        self.transactions_path = Path(transactions_path)
        self.identity_path = Path(identity_path)
        self.chunk_size = chunk_size

        self._identity: dict[str, dict[str, Any]] | None = None
        self._transaction_cache: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _normalize_id(value: Any) -> str:
        if value is None:
            return ""

        text = str(value).strip()

        if text.endswith(".0"):
            numeric_part = text[:-2]
            if numeric_part.isdigit():
                return numeric_part

        return text

    @staticmethod
    def _clean_value(value: Any) -> Any:
        if pd.isna(value):
            return None

        if isinstance(value, pd.Timestamp):
            return value.isoformat()

        if hasattr(value, "item"):
            try:
                return value.item()
            except (ValueError, TypeError):
                pass

        return value

    def _load_identity(self) -> None:
        if self._identity is not None:
            return

        if not self.identity_path.exists():
            raise FileNotFoundError(
                f"Identity dataset not found: {self.identity_path}"
            )

        header = pd.read_csv(
            self.identity_path,
            nrows=0,
        )

        columns = [
            column
            for column in self.IDENTITY_COLUMNS
            if column in header.columns
        ]

        if "TransactionID" not in columns:
            raise ValueError(
                "identity.csv does not contain TransactionID."
            )

        frame = pd.read_csv(
            self.identity_path,
            usecols=columns,
        )

        identity: dict[str, dict[str, Any]] = {}

        for row in frame.to_dict(orient="records"):
            transaction_id = self._normalize_id(
                row.get("TransactionID")
            )

            if not transaction_id:
                continue

            identity[transaction_id] = {
                key: self._clean_value(value)
                for key, value in row.items()
                if key != "TransactionID"
            }

        self._identity = identity

    def get_transaction(
        self,
        transaction_id: str | int,
    ) -> dict[str, Any]:
        """Return one complete transaction record."""

        normalized_id = self._normalize_id(transaction_id)

        if not normalized_id:
            raise ValueError("TransactionID is required.")

        if normalized_id in self._transaction_cache:
            return dict(self._transaction_cache[normalized_id])

        if not self.transactions_path.exists():
            raise FileNotFoundError(
                f"Transaction dataset not found: "
                f"{self.transactions_path}"
            )

        header = pd.read_csv(
            self.transactions_path,
            nrows=0,
        )

        if "TransactionID" not in header.columns:
            raise ValueError(
                "transactions.csv does not contain TransactionID."
            )

        found: dict[str, Any] | None = None

        for chunk in pd.read_csv(
            self.transactions_path,
            chunksize=self.chunk_size,
        ):
            ids = chunk["TransactionID"].map(
                self._normalize_id
            )

            matches = chunk.loc[
                ids == normalized_id
            ]

            if not matches.empty:
                found = matches.iloc[0].to_dict()
                break

        if found is None:
            raise KeyError(
                f"Transaction not found: {normalized_id}"
            )

        record = {
            key: self._clean_value(value)
            for key, value in found.items()
        }

        record["TransactionID"] = normalized_id

        self._load_identity()

        identity_record = (
            self._identity.get(normalized_id, {})
            if self._identity is not None
            else {}
        )

        for key, value in identity_record.items():
            if (
                key not in record
                or record[key] is None
            ):
                record[key] = value

        self._transaction_cache[normalized_id] = dict(record)

        return record

    def clear_cache(self) -> None:
        """Clear cached transaction and identity records."""

        self._transaction_cache.clear()
        self._identity = None