"""
HHGOA dataset preprocessing utilities.

Converts raw HHGOA/IEEE-CIS style records into normalized, graph-ready
records without inventing relationships that are not explicitly supported
by the source data.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd


NULL_VALUES = {"", "nan", "none", "null", "nat", "na", "n/a"}


def _clean_value(value: Any) -> Any:
    """Normalize scalar values while preserving useful numeric types."""
    if value is None:
        return None

    if pd.isna(value):
        return None

    if isinstance(value, str):
        value = value.strip()
        if value.lower() in NULL_VALUES:
            return None
        return value

    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()

    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass

    return value


def _normalize_identifier(value: Any) -> str | None:
    """Create a stable identifier representation."""
    value = _clean_value(value)

    if value is None:
        return None

    if isinstance(value, float) and value.is_integer():
        value = int(value)

    text = str(value).strip()

    if not text:
        return None

    text = re.sub(r"\s+", "_", text)
    return text


def _find_column(
    columns: Iterable[str],
    candidates: Iterable[str],
) -> str | None:
    """Find a column using case-insensitive matching."""
    normalized = {
        str(column).strip().lower(): str(column)
        for column in columns
    }

    for candidate in candidates:
        match = normalized.get(candidate.lower())
        if match:
            return match

    return None


def _records_from_dataframe(
    dataframe: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Convert a dataframe into JSON-safe dictionaries."""
    records: list[dict[str, Any]] = []

    for row in dataframe.to_dict(orient="records"):
        cleaned = {
            str(key): _clean_value(value)
            for key, value in row.items()
        }
        records.append(cleaned)

    return records


def normalize_transactions(
    dataframe: pd.DataFrame,
) -> list[dict[str, Any]]:
    """
    Normalize transaction rows.

    The function preserves original fields and adds stable graph-oriented
    identifiers when the corresponding source fields exist.
    """
    records = _records_from_dataframe(dataframe)

    transaction_column = _find_column(
        dataframe.columns,
        ("TransactionID", "transaction_id", "TransactionId", "transactionid"),
    )

    customer_column = _find_column(
        dataframe.columns,
        ("CustomerID", "customer_id", "CustomerId", "customerid"),
    )

    device_column = _find_column(
        dataframe.columns,
        ("DeviceID", "device_id", "DeviceId", "deviceid"),
    )

    ip_column = _find_column(
        dataframe.columns,
        ("IPAddress", "IP", "ip_address", "ip"),
    )

    for index, record in enumerate(records):
        transaction_id = (
            _normalize_identifier(record.get(transaction_column))
            if transaction_column
            else None
        )

        if transaction_id is None:
            transaction_id = f"ROW_{index + 1}"

        record["transaction_id"] = transaction_id

        if customer_column:
            customer_id = _normalize_identifier(
                record.get(customer_column)
            )
            if customer_id:
                record["customer_id"] = customer_id

        if device_column:
            device_id = _normalize_identifier(record.get(device_column))
            if device_id:
                record["device_id"] = device_id

        if ip_column:
            ip_address = _normalize_identifier(record.get(ip_column))
            if ip_address:
                record["ip_address"] = ip_address

    return records


def build_graph_records(
    transactions: Iterable[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Build graph-ready vertex and edge records.

    Relationships are created only when the source transaction explicitly
    contains the relevant entity identifier.
    """
    customers: dict[str, dict[str, Any]] = {}
    devices: dict[str, dict[str, Any]] = {}
    connections: dict[str, dict[str, Any]] = {}
    transaction_records: dict[str, dict[str, Any]] = {}

    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str]] = set()

    def add_edge(
        source: str,
        target: str,
        edge_type: str,
        properties: Mapping[str, Any] | None = None,
    ) -> None:
        key = (source, target, edge_type)

        if key in seen_edges:
            return

        seen_edges.add(key)

        edges.append(
            {
                "source": source,
                "target": target,
                "type": edge_type,
                "properties": dict(properties or {}),
            }
        )

    for transaction in transactions:
        transaction_id = _normalize_identifier(
            transaction.get("transaction_id")
        )

        if not transaction_id:
            continue

        transaction_records[transaction_id] = dict(transaction)

        customer_id = _normalize_identifier(
            transaction.get("customer_id")
        )

        if customer_id:
            customers.setdefault(
                customer_id,
                {
                    "customer_id": customer_id,
                },
            )

            add_edge(
                f"customer:{customer_id}",
                f"transaction:{transaction_id}",
                "MADE_TRANSACTION",
            )

        device_id = _normalize_identifier(
            transaction.get("device_id")
        )

        if device_id:
            devices.setdefault(
                device_id,
                {
                    "device_id": device_id,
                },
            )

            add_edge(
                f"device:{device_id}",
                f"transaction:{transaction_id}",
                "USED_FOR_TRANSACTION",
            )

        ip_address = _normalize_identifier(
            transaction.get("ip_address")
        )

        if ip_address:
            connection_id = f"ip:{ip_address}"

            connections.setdefault(
                connection_id,
                {
                    "connection_id": connection_id,
                    "connection_type": "IP",
                    "value": ip_address,
                },
            )

            add_edge(
                connection_id,
                f"transaction:{transaction_id}",
                "CONNECTED_TO_TRANSACTION",
            )

    return {
        "customers": list(customers.values()),
        "devices": list(devices.values()),
        "connections": list(connections.values()),
        "transactions": list(transaction_records.values()),
        "edges": edges,
    }


def preprocess_file(
    input_path: Path,
    output_dir: Path,
) -> dict[str, int]:
    """Preprocess one CSV file and write normalized graph-ready JSON."""
    dataframe = pd.read_csv(input_path, low_memory=False)

    transactions = normalize_transactions(dataframe)
    graph = build_graph_records(transactions)

    output_dir.mkdir(parents=True, exist_ok=True)

    transaction_output = output_dir / "transactions.normalized.jsonl"

    with transaction_output.open("w", encoding="utf-8") as file:
        for transaction in transactions:
            file.write(
                json.dumps(
                    transaction,
                    ensure_ascii=False,
                    default=str,
                )
                + "\n"
            )

    graph_output = output_dir / "graph_records.json"

    graph_output.write_text(
        json.dumps(
            graph,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    return {
        "input_rows": len(dataframe),
        "transactions": len(graph["transactions"]),
        "customers": len(graph["customers"]),
        "devices": len(graph["devices"]),
        "connections": len(graph["connections"]),
        "edges": len(graph["edges"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preprocess HHGOA transaction data."
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to the raw HHGOA CSV file.",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory for normalized graph-ready data.",
    )

    args = parser.parse_args()

    summary = preprocess_file(
        input_path=args.input,
        output_dir=args.output_dir,
    )

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()