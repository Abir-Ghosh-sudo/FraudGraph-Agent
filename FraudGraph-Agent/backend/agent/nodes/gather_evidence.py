from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_id(value: Any) -> str | None:
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    if value.endswith(".0"):
        value = value[:-2]

    return value


def _transaction_value(
    transaction: dict[str, Any],
    *keys: str,
) -> Any:
    for key in keys:
        value = transaction.get(key)

        if value is not None and value != "":
            return value

    return None


def _append_unique_evidence(
    existing: list[dict[str, Any]],
    new_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result = list(existing)

    existing_ids = {
        str(item.get("evidence_id"))
        for item in result
        if isinstance(item, dict)
        and item.get("evidence_id") is not None
    }

    for item in new_items:
        if not isinstance(item, dict):
            continue

        evidence_id = item.get("evidence_id")

        if evidence_id is None:
            continue

        evidence_id = str(evidence_id)

        if evidence_id in existing_ids:
            continue

        result.append(item)
        existing_ids.add(evidence_id)

    return result


def _build_customer_evidence(
    *,
    customer_id: str | None,
    card_id: str | None,
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []

    if customer_id:
        evidence.append(
            {
                "evidence_id": f"customer-context-{customer_id}",
                "source_type": "CUSTOMER",
                "evidence_type": "CONTEXTUAL",
                "title": "Customer investigation context",
                "description": (
                    f"The investigation is associated with "
                    f"customer {customer_id}."
                ),
                "data": {
                    "customer_id": customer_id,
                    "card_id": card_id,
                },
                "confidence": 0.95,
            }
        )

    if card_id:
        evidence.append(
            {
                "evidence_id": f"card-context-{card_id}",
                "source_type": "ACCOUNT",
                "evidence_type": "CONTEXTUAL",
                "title": "Card investigation context",
                "description": (
                    f"The investigated transaction is associated "
                    f"with card {card_id}."
                ),
                "data": {
                    "card_id": card_id,
                    "customer_id": customer_id,
                },
                "confidence": 0.95,
            }
        )

    return evidence


def _build_transaction_context_evidence(
    transaction: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []

    transaction_id = _clean_id(
        _transaction_value(
            transaction,
            "TransactionID",
            "transaction_id",
        )
    )

    if not transaction_id:
        return evidence

    amount = _transaction_value(
        transaction,
        "TransactionAmt",
        "transaction_amount",
    )

    channel = _transaction_value(
        transaction,
        "channel",
    )

    timestamp = _transaction_value(
        transaction,
        "ts",
    )

    product = _transaction_value(
        transaction,
        "ProductCD",
        "product",
    )

    if amount is not None:
        evidence.append(
            {
                "evidence_id": f"transaction-amount-{transaction_id}",
                "source_type": "TRANSACTION",
                "evidence_type": "DIRECT",
                "title": "Transaction amount",
                "description": (
                    f"Transaction {transaction_id} has amount "
                    f"{amount}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "amount": amount,
                },
                "confidence": 0.98,
            }
        )

    if channel:
        evidence.append(
            {
                "evidence_id": f"transaction-channel-{transaction_id}",
                "source_type": "TRANSACTION",
                "evidence_type": "CONTEXTUAL",
                "title": "Transaction channel",
                "description": (
                    f"Transaction {transaction_id} used "
                    f"channel {channel}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "channel": channel,
                },
                "confidence": 0.95,
            }
        )

    if timestamp:
        evidence.append(
            {
                "evidence_id": f"transaction-time-{transaction_id}",
                "source_type": "TRANSACTION",
                "evidence_type": "DIRECT",
                "title": "Transaction time",
                "description": (
                    f"Transaction {transaction_id} occurred at "
                    f"{timestamp}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "timestamp": timestamp,
                },
                "confidence": 0.98,
            }
        )

    if product:
        evidence.append(
            {
                "evidence_id": f"transaction-product-{transaction_id}",
                "source_type": "TRANSACTION",
                "evidence_type": "CONTEXTUAL",
                "title": "Transaction product",
                "description": (
                    f"Transaction {transaction_id} has "
                    f"product category {product}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "product": product,
                },
                "confidence": 0.90,
            }
        )

    return evidence


def _build_identity_evidence(
    transaction: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []

    transaction_id = _clean_id(
        _transaction_value(
            transaction,
            "TransactionID",
            "transaction_id",
        )
    )

    if not transaction_id:
        return evidence

    device_type = _transaction_value(
        transaction,
        "DeviceType",
    )

    device_info = _transaction_value(
        transaction,
        "DeviceInfo",
    )

    addr1 = _transaction_value(
        transaction,
        "addr1",
    )

    addr2 = _transaction_value(
        transaction,
        "addr2",
    )

    ip = _transaction_value(
        transaction,
        "ip",
        "IP",
    )

    if device_type:
        evidence.append(
            {
                "evidence_id": f"identity-device-type-{transaction_id}",
                "source_type": "DEVICE",
                "evidence_type": "DIRECT",
                "title": "Device type",
                "description": (
                    f"Device type associated with transaction "
                    f"{transaction_id}: {device_type}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "device_type": device_type,
                },
                "confidence": 0.92,
            }
        )

    if device_info:
        evidence.append(
            {
                "evidence_id": f"identity-device-info-{transaction_id}",
                "source_type": "DEVICE",
                "evidence_type": "DIRECT",
                "title": "Device information",
                "description": (
                    f"Device information is available for "
                    f"transaction {transaction_id}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "device_info": str(device_info),
                },
                "confidence": 0.88,
            }
        )

    if addr1 is not None or addr2 is not None:
        evidence.append(
            {
                "evidence_id": f"identity-address-{transaction_id}",
                "source_type": "ACCOUNT",
                "evidence_type": "CONTEXTUAL",
                "title": "Address context",
                "description": (
                    f"Address-related transaction fields are "
                    f"available for transaction {transaction_id}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "addr1": addr1,
                    "addr2": addr2,
                },
                "confidence": 0.75,
            }
        )

    if ip:
        evidence.append(
            {
                "evidence_id": f"identity-ip-{transaction_id}",
                "source_type": "CONNECTION",
                "evidence_type": "DIRECT",
                "title": "IP/connection information",
                "description": (
                    f"Connection information is available for "
                    f"transaction {transaction_id}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "ip": ip,
                },
                "confidence": 0.90,
            }
        )

    return evidence


def _extract_existing_graph_evidence(
    state: dict[str, Any],
) -> list[dict[str, Any]]:
    graph_evidence = state.get("graph_evidence")

    if not isinstance(graph_evidence, list):
        return []

    return [
        item
        for item in graph_evidence
        if isinstance(item, dict)
    ]


def _extract_existing_historical_evidence(
    state: dict[str, Any],
) -> list[dict[str, Any]]:
    historical = state.get("historical_evidence")

    if not isinstance(historical, list):
        return []

    return [
        item
        for item in historical
        if isinstance(item, dict)
    ]


def gather_evidence(
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Collect and normalize currently available investigation evidence.

    This stage does not decide whether the transaction is fraudulent.

    It prepares evidence for:
        transaction -> identity/device/IP -> graph -> history
        -> pattern detection -> risk assessment
    """

    result = dict(state)

    result["current_stage"] = "GATHER_EVIDENCE"
    result["status"] = "INVESTIGATING"

    transaction = result.get("transaction")

    if not isinstance(transaction, dict):
        result["warnings"] = [
            *list(result.get("warnings") or []),
            "No transaction context available for evidence gathering.",
        ]

        result["requires_additional_evidence"] = True

        return result

    customer_id = _clean_id(
        result.get("customer_id")
        or transaction.get("customer_id")
    )

    card_id = _clean_id(
        result.get("card_id")
        or transaction.get("card_id")
    )

    transaction_id = _clean_id(
        result.get("transaction_id")
        or transaction.get("TransactionID")
        or transaction.get("transaction_id")
    )

    if customer_id:
        result["customer_id"] = customer_id

    if card_id:
        result["card_id"] = card_id

    if transaction_id:
        result["transaction_id"] = transaction_id

    # ---------------------------------------------------------------
    # Build locally available evidence.
    # ---------------------------------------------------------------
    transaction_evidence = _build_transaction_context_evidence(
        transaction
    )

    identity_evidence = _build_identity_evidence(
        transaction
    )

    customer_evidence = _build_customer_evidence(
        customer_id=customer_id,
        card_id=card_id,
    )

    new_evidence = [
        *transaction_evidence,
        *identity_evidence,
        *customer_evidence,
    ]

    # ---------------------------------------------------------------
    # Include evidence already gathered by graph/history retrievers.
    # ---------------------------------------------------------------
    graph_evidence = _extract_existing_graph_evidence(
        result
    )

    historical_evidence = _extract_existing_historical_evidence(
        result
    )

    new_evidence.extend(graph_evidence)
    new_evidence.extend(historical_evidence)

    existing_evidence = [
        item
        for item in (result.get("evidence") or [])
        if isinstance(item, dict)
    ]

    merged_evidence = _append_unique_evidence(
        existing_evidence,
        new_evidence,
    )

    result["evidence"] = merged_evidence

    result["evidence_ids"] = [
        str(item["evidence_id"])
        for item in merged_evidence
        if item.get("evidence_id") is not None
    ]

    # ---------------------------------------------------------------
    # Keep separate evidence buckets for downstream reasoning.
    # ---------------------------------------------------------------
    result["graph_evidence"] = graph_evidence
    result["historical_evidence"] = historical_evidence

    # ---------------------------------------------------------------
    # Record evidence summary.
    # ---------------------------------------------------------------
    evidence_sources: dict[str, int] = {}

    for item in merged_evidence:
        source_type = str(
            item.get("source_type") or "UNKNOWN"
        )

        evidence_sources[source_type] = (
            evidence_sources.get(source_type, 0) + 1
        )

    result["evidence_summary"] = {
        "total": len(merged_evidence),
        "sources": evidence_sources,
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "card_id": card_id,
    }

    # ---------------------------------------------------------------
    # Evidence sufficiency is deliberately conservative.
    #
    # Having a bank risk score alone is NOT enough.
    # At this stage we want multiple independent evidence sources.
    # ---------------------------------------------------------------
    independent_sources = set()

    for item in merged_evidence:
        source_type = item.get("source_type")

        if source_type:
            independent_sources.add(
                str(source_type)
            )

    has_transaction = (
        "TRANSACTION" in independent_sources
    )

    has_identity = bool(
        independent_sources.intersection(
            {
                "DEVICE",
                "CONNECTION",
                "ACCOUNT",
                "CUSTOMER",
            }
        )
    )

    has_graph = "GRAPH" in independent_sources
    has_history = (
        "HISTORICAL_CASE" in independent_sources
        or bool(historical_evidence)
    )

    sufficient = (
        len(independent_sources) >= 3
        or (
            has_transaction
            and has_identity
            and (has_graph or has_history)
        )
    )

    result["evidence_sufficient"] = sufficient

    # Do not automatically request customer verification here.
    # Later uncertainty/policy stages decide whether additional
    # evidence is actually required.
    result["requires_additional_evidence"] = not sufficient

    if not sufficient:
        result["required_evidence"] = [
            *list(result.get("required_evidence") or []),
            "additional independent transaction/entity evidence",
        ]

    # ---------------------------------------------------------------
    # Event
    # ---------------------------------------------------------------
    now = _utc_now()

    events = list(result.get("events") or [])

    events.append(
        {
            "event_id": (
                f"evidence-{transaction_id or 'unknown'}-{now}"
            ),
            "event_type": "EVIDENCE_FOUND",
            "investigation_id": result.get(
                "investigation_id"
            ),
            "case_id": result.get("case_id"),
            "stage": "GATHER_EVIDENCE",
            "message": (
                f"Collected {len(merged_evidence)} evidence items "
                f"from {len(independent_sources)} source types."
            ),
            "payload": {
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "card_id": card_id,
                "evidence_count": len(merged_evidence),
                "independent_sources": sorted(
                    independent_sources
                ),
                "evidence_sufficient": sufficient,
                "requires_additional_evidence": (
                    not sufficient
                ),
            },
            "created_at": now,
        }
    )

    result["events"] = events

    result["progress"] = max(
        float(result.get("progress") or 0.0),
        0.35,
    )

    return result


def run(state: dict[str, Any]) -> dict[str, Any]:
    return gather_evidence(state)
class GatherEvidenceNode:
    def __init__(self, settings=None):
        self.settings = settings

    def __call__(self, state):
        return gather_evidence(state)

    def run(self, state):
        return gather_evidence(state)
