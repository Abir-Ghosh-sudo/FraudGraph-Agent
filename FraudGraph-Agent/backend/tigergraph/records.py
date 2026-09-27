"""Translate raw CSV rows into TigerGraph vertex and edge upserts.

Every identifier and attribute here is read directly from the dataset in
``data/raw``. Vertex and edge names follow the schema published in
``data/raw/README.md``.

The ``Transaction`` vertex is keyed by transaction id, and the chain of
``NEXT`` edges is emitted per card in file order, which is chronological
order in this dataset.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

_TRANSACTION_COLUMNS = (
    "TransactionID",
    "TransactionAmt",
    "TransactionDT",
    "ProductCD",
    "customer_id",
    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",
    "addr1",
    "P_emaildomain",
    "R_emaildomain",
    "isFraud",
)

_IDENTITY_COLUMNS = ("TransactionID", "DeviceInfo", "DeviceType")


def _clean(value: Any) -> Any:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    if text.endswith(".0") and text[:-2].lstrip("-").isdigit():
        return text[:-2]
    return text


def _as_float(value: Any) -> float | None:
    text = _clean(value)
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _as_int(value: Any) -> int | None:
    number = _as_float(value)
    return int(number) if number is not None else None


@dataclass
class RecordBatch:
    """A batch of upserts for one window of the dataset."""

    vertices: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)


def _read_identity(identity_csv: Path) -> dict[str, dict[str, str]]:
    if not identity_csv.exists():
        return {}
    out: dict[str, dict[str, str]] = {}
    with identity_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        available = set(reader.fieldnames or ())
        if "TransactionID" not in available:
            return {}
        wanted = [c for c in _IDENTITY_COLUMNS if c in available]
        for row in reader:
            tid = _clean(row.get("TransactionID"))
            device = _clean(row.get("DeviceInfo"))
            if not tid or not device:
                continue
            out[str(tid)] = {
                "device_info": str(device),
                "device_type": str(_clean(row.get("DeviceType")) or ""),
            }
    return out


def iter_graph_records(
    *,
    transactions_csv: Path,
    identity_csv: Path,
    max_rows: int,
    batch_size: int = 1_000,
) -> Iterator[RecordBatch]:
    """Yield batches of vertex/edge upserts derived from the dataset."""
    if not transactions_csv.exists():
        raise FileNotFoundError(
            f"Transaction dataset not found: {transactions_csv}"
        )

    devices = _read_identity(identity_csv)
    batch = RecordBatch()
    seen_edges: set[tuple[str, str, str]] = set()
    last_txn_by_card: dict[str, str] = {}
    emitted = 0

    def flush() -> RecordBatch | None:
        nonlocal batch
        if not batch.vertices and not batch.edges:
            return None
        current = batch
        batch = RecordBatch()
        return current

    with transactions_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        available = set(reader.fieldnames or ())
        wanted = [c for c in _TRANSACTION_COLUMNS if c in available]

        for row in reader:
            if emitted >= max_rows:
                break
            emitted += 1

            transaction_id = _clean(row.get("TransactionID"))
            if not transaction_id:
                continue
            transaction_id = str(transaction_id)

            amount = _as_float(row.get("TransactionAmt"))
            risk = _as_float(row.get("risk_score"))
            is_fraud = _clean(row.get("isFraud"))

            batch.vertices.append(
                {
                    "vertex_type": "Transaction",
                    "vertex_id": transaction_id,
                    "attributes": {
                        "amount": amount,
                        "product_cd": _clean(row.get("ProductCD")),
                        "risk_score": risk,
                        "ts": _as_int(row.get("TransactionDT")),
                        "is_fraud": (
                            str(is_fraud).lower() in {"1", "true", "yes"}
                            if is_fraud is not None
                            else None
                        ),
                    },
                }
            )

            customer = _clean(row.get("customer_id"))
            if customer:
                batch.vertices.append(
                    {
                        "vertex_type": "Customer",
                        "vertex_id": str(customer),
                        "attributes": {"customer_id": str(customer)},
                    }
                )

            cards = [str(_clean(row.get(f"card{i}"))) for i in range(1, 7)]
            cards = [c for c in cards if c]
            for card in cards:
                batch.vertices.append(
                    {
                        "vertex_type": "Card",
                        "vertex_id": card,
                        "attributes": {"card_id": card},
                    }
                )

            if customer and cards:
                for card in cards:
                    key = ("OWNS", str(customer), card)
                    if key not in seen_edges:
                        seen_edges.add(key)
                        batch.edges.append(
                            {
                                "edge_type": "OWNS",
                                "from_id": str(customer),
                                "to_id": card,
                            }
                        )

            for card in cards:
                key = ("MADE", card, transaction_id)
                if key not in seen_edges:
                    seen_edges.add(key)
                    batch.edges.append(
                        {
                            "edge_type": "MADE",
                            "from_id": card,
                            "to_id": transaction_id,
                        }
                    )
                # NEXT follows the per-card chronology of the file.
                previous = last_txn_by_card.get(card)
                if previous and previous != transaction_id:
                    nkey = ("NEXT", previous, transaction_id)
                    if nkey not in seen_edges:
                        seen_edges.add(nkey)
                        batch.edges.append(
                            {
                                "edge_type": "NEXT",
                                "from_id": previous,
                                "to_id": transaction_id,
                            }
                        )
                last_txn_by_card[card] = transaction_id

            domain = _clean(row.get("P_emaildomain"))
            if domain:
                batch.vertices.append(
                    {
                        "vertex_type": "EmailDomain",
                        "vertex_id": str(domain),
                        "attributes": {"domain": str(domain)},
                    }
                )
                key = ("PURCHASER_EMAIL", transaction_id, str(domain))
                if key not in seen_edges:
                    seen_edges.add(key)
                    batch.edges.append(
                        {
                            "edge_type": "PURCHASER_EMAIL",
                            "from_id": transaction_id,
                            "to_id": str(domain),
                        }
                    )

            region = _clean(row.get("addr1"))
            if region:
                batch.vertices.append(
                    {
                        "vertex_type": "BillingRegion",
                        "vertex_id": str(region),
                        "attributes": {"region": str(region)},
                    }
                )
                key = ("BILLED_IN", transaction_id, str(region))
                if key not in seen_edges:
                    seen_edges.add(key)
                    batch.edges.append(
                        {
                            "edge_type": "BILLED_IN",
                            "from_id": transaction_id,
                            "to_id": str(region),
                        }
                    )

            device = devices.get(transaction_id)
            if device:
                device_id = device["device_info"]
                batch.vertices.append(
                    {
                        "vertex_type": "DeviceProfile",
                        "vertex_id": device_id,
                        "attributes": {
                            "device_info": device_id,
                            "device_type": device.get("device_type") or None,
                        },
                    }
                )
                key = ("FROM_DEVICE", transaction_id, device_id)
                if key not in seen_edges:
                    seen_edges.add(key)
                    batch.edges.append(
                        {
                            "edge_type": "FROM_DEVICE",
                            "from_id": transaction_id,
                            "to_id": device_id,
                        }
                    )

            if len(batch.vertices) >= batch_size:
                out = flush()
                if out is not None:
                    yield out

    out = flush()
    if out is not None:
        yield out


def iter_closed_case_records(
    *,
    closed_cases_csv: Path,
) -> Iterator[RecordBatch]:
    """Build ClosedCase vertices and their edges from the closed-case history."""
    if not closed_cases_csv.exists():
        return

    with closed_cases_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        batch = RecordBatch()

        for row in reader:
            case_id = _clean(row.get("case_id"))
            if not case_id:
                continue
            case_id = str(case_id)

            batch.vertices.append(
                {
                    "vertex_type": "ClosedCase",
                    "vertex_id": case_id,
                    "attributes": {
                        "case_id": case_id,
                        "outcome": _clean(row.get("outcome")),
                        "pattern": _clean(row.get("pattern")),
                        "opened_at": _clean(row.get("opened_at")),
                        "closed_at": _clean(row.get("closed_at")),
                        "n_txns": _as_int(row.get("n_txns")),
                        "exposure_usd": _as_float(row.get("exposure_usd")),
                        "report_filed": (
                            str(_clean(row.get("report_filed"))).lower()
                            in {"1", "true", "yes"}
                            if _clean(row.get("report_filed")) is not None
                            else None
                        ),
                    },
                }
            )

            for raw in str(row.get("txn_ids") or "").split(";"):
                txn = _clean(raw)
                if txn:
                    batch.edges.append(
                        {
                            "edge_type": "INVOLVES",
                            "from_id": case_id,
                            "to_id": str(txn),
                        }
                    )

            for raw in str(row.get("connected_card_ids") or "").split(";"):
                card = _clean(raw)
                if card:
                    batch.edges.append(
                        {
                            "edge_type": "CONNECTED_TO",
                            "from_id": case_id,
                            "to_id": str(card),
                        }
                    )

            if len(batch.vertices) >= 1_000:
                yield batch
                batch = RecordBatch()

        if batch.vertices:
            yield batch


__all__ = [
    "RecordBatch",
    "iter_closed_case_records",
    "iter_graph_records",
]
