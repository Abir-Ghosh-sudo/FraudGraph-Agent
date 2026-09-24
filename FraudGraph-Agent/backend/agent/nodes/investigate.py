from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.ml.transaction_loader import TransactionRecordLoader


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


def _transaction_id_from_state(
    state: dict[str, Any],
) -> str | None:
    candidates = (
        state.get("transaction_id"),
        state.get("flagged_txn_id"),
    )

    transaction = state.get("transaction")

    if isinstance(transaction, dict):
        candidates += (
            transaction.get("TransactionID"),
            transaction.get("transaction_id"),
        )

    trigger = state.get("trigger")

    if isinstance(trigger, dict):
        candidates += (
            trigger.get("transaction_id"),
            trigger.get("flagged_txn_id"),
        )

    for candidate in candidates:
        cleaned = _clean_id(candidate)

        if cleaned:
            return cleaned

    return None


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_transaction_evidence(
    transaction: dict[str, Any],
) -> list[dict[str, Any]]:
    transaction_id = _clean_id(
        transaction.get("TransactionID")
        or transaction.get("transaction_id")
    )

    if not transaction_id:
        return []

    evidence: list[dict[str, Any]] = []

    risk_score = _safe_float(
        transaction.get("risk_score")
    )

    if risk_score is not None:
        evidence.append(
            {
                "evidence_id": (
                    f"txn-risk-{transaction_id}"
                ),
                "source_type": "TRANSACTION",
                "evidence_type": "DIRECT",
                "title": "Bank transaction risk score",
                "description": (
                    f"Bank fraud model risk score for transaction "
                    f"{transaction_id} is {risk_score:.4f}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "risk_score": risk_score,
                },
                "confidence": 0.60,
            }
        )

    amount = _safe_float(
        transaction.get("TransactionAmt")
        or transaction.get("transaction_amount")
    )

    if amount is not None:
        evidence.append(
            {
                "evidence_id": (
                    f"txn-amount-{transaction_id}"
                ),
                "source_type": "TRANSACTION",
                "evidence_type": "DIRECT",
                "title": "Transaction amount",
                "description": (
                    f"Transaction amount is {amount:.2f}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "amount": amount,
                },
                "confidence": 0.95,
            }
        )

    channel = transaction.get("channel")

    if channel:
        evidence.append(
            {
                "evidence_id": (
                    f"txn-channel-{transaction_id}"
                ),
                "source_type": "TRANSACTION",
                "evidence_type": "CONTEXTUAL",
                "title": "Transaction channel",
                "description": (
                    f"Transaction channel is {channel}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "channel": channel,
                },
                "confidence": 0.90,
            }
        )

    timestamp = transaction.get("ts")

    if timestamp:
        evidence.append(
            {
                "evidence_id": (
                    f"txn-time-{transaction_id}"
                ),
                "source_type": "TRANSACTION",
                "evidence_type": "DIRECT",
                "title": "Transaction timestamp",
                "description": (
                    f"Transaction occurred at {timestamp}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "timestamp": timestamp,
                },
                "confidence": 0.95,
            }
        )

    return evidence


def _build_identity_evidence(
    transaction: dict[str, Any],
) -> list[dict[str, Any]]:
    transaction_id = _clean_id(
        transaction.get("TransactionID")
        or transaction.get("transaction_id")
    )

    if not transaction_id:
        return []

    evidence: list[dict[str, Any]] = []

    device_type = transaction.get("DeviceType")

    if device_type:
        evidence.append(
            {
                "evidence_id": (
                    f"device-type-{transaction_id}"
                ),
                "source_type": "DEVICE",
                "evidence_type": "DIRECT",
                "title": "Device type",
                "description": (
                    f"Transaction {transaction_id} is associated "
                    f"with device type {device_type}."
                ),
                "data": {
                    "transaction_id": transaction_id,
                    "device_type": device_type,
                },
                "confidence": 0.90,
            }
        )

    device_info = transaction.get("DeviceInfo")

    if device_info:
        evidence.append(
            {
                "evidence_id": (
                    f"device-info-{transaction_id}"
                ),
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
                "confidence": 0.85,
            }
        )

    return evidence


def _build_customer_context(
    state: dict[str, Any],
    transaction: dict[str, Any],
) -> dict[str, Any]:
    customer_id = _clean_id(
        state.get("customer_id")
        or transaction.get("customer_id")
    )

    card_id = _clean_id(
        state.get("card_id")
        or transaction.get("card_id")
    )

    context: dict[str, Any] = {}

    if customer_id:
        context["customer_id"] = customer_id

    if card_id:
        context["card_id"] = card_id

    return context


def investigate(state: dict[str, Any]) -> dict[str, Any]:
    """
    Load the actual transaction and establish the initial investigation
    context.

    Important:
    - flagged_txn_id is an investigation starting point, not a fraud label.
    - No fraud verdict is produced here.
    - ML prediction is intentionally left to assess_risk.py.
    - Graph/pattern investigation happens in later stages.
    """

    result = dict(state)

    transaction_id = _transaction_id_from_state(state)

    now = _utc_now()

    result["current_stage"] = "INVESTIGATE"
    result["status"] = "INVESTIGATING"

    if not transaction_id:
        result["error"] = (
            "Investigation cannot start because no transaction ID "
            "was supplied."
        )

        result["warnings"] = [
            *list(result.get("warnings") or []),
            "Missing transaction identifier.",
        ]

        return result

    result["transaction_id"] = transaction_id
    result["flagged_txn_id"] = transaction_id

    loader = TransactionRecordLoader(
        transactions_path="data/raw/transactions.csv",
        identity_path="data/raw/identity.csv",
    )

    transaction: dict[str, Any] | None = None

    try:
        transaction = loader.get_transaction(
            transaction_id
        )
    except Exception as exc:
        result["error"] = (
            f"Failed to load transaction {transaction_id}: "
            f"{exc}"
        )

        result["warnings"] = [
            *list(result.get("warnings") or []),
            "Transaction lookup failed.",
        ]

        return result

    if not transaction:
        result["error"] = (
            f"Transaction {transaction_id} was not found "
            "in the transaction dataset."
        )

        result["warnings"] = [
            *list(result.get("warnings") or []),
            f"Transaction {transaction_id} not found.",
        ]

        return result

    result["transaction"] = transaction

    # ------------------------------------------------------------------
    # Synchronise primary identifiers from the actual transaction.
    # Existing explicit state values take precedence.
    # ------------------------------------------------------------------
    if not result.get("customer_id"):
        customer_id = _clean_id(
            transaction.get("customer_id")
        )

        if customer_id:
            result["customer_id"] = customer_id

    if not result.get("card_id"):
        card_id = _clean_id(
            transaction.get("card_id")
        )

        if card_id:
            result["card_id"] = card_id

    # ------------------------------------------------------------------
    # Preserve the bank-provided risk score as an input signal.
    # It is NOT treated as ground truth.
    # ------------------------------------------------------------------
    bank_risk_score = _safe_float(
        transaction.get("risk_score")
    )

    if bank_risk_score is not None:
        result["bank_risk_score"] = max(
            0.0,
            min(1.0, bank_risk_score),
        )

    # ------------------------------------------------------------------
    # Initial transaction + identity evidence.
    # ------------------------------------------------------------------
    transaction_evidence = _build_transaction_evidence(
        transaction
    )

    identity_evidence = _build_identity_evidence(
        transaction
    )

    new_evidence = [
        *transaction_evidence,
        *identity_evidence,
    ]

    existing_evidence = list(
        result.get("evidence") or []
    )

    existing_ids = {
        str(item.get("evidence_id"))
        for item in existing_evidence
        if isinstance(item, dict)
        and item.get("evidence_id") is not None
    }

    for item in new_evidence:
        evidence_id = str(
            item.get("evidence_id")
        )

        if evidence_id not in existing_ids:
            existing_evidence.append(item)
            existing_ids.add(evidence_id)

    result["evidence"] = existing_evidence
    result["evidence_ids"] = [
        str(item["evidence_id"])
        for item in existing_evidence
        if isinstance(item, dict)
        and item.get("evidence_id") is not None
    ]

    # ------------------------------------------------------------------
    # Customer/card context for downstream graph and evidence stages.
    # ------------------------------------------------------------------
    result["investigation_context"] = _build_customer_context(
        state,
        transaction,
    )

    # ------------------------------------------------------------------
    # Event
    # ------------------------------------------------------------------
    events = list(result.get("events") or [])

    events.append(
        {
            "event_id": (
                f"investigate-{transaction_id}-{now}"
            ),
            "event_type": "STAGE_STARTED",
            "investigation_id": result.get(
                "investigation_id"
            ),
            "case_id": result.get("case_id"),
            "stage": "INVESTIGATE",
            "message": (
                f"Loaded transaction {transaction_id} and "
                "established investigation context."
            ),
            "payload": {
                "transaction_id": transaction_id,
                "customer_id": result.get("customer_id"),
                "card_id": result.get("card_id"),
                "bank_risk_score": result.get(
                    "bank_risk_score"
                ),
                "evidence_count": len(new_evidence),
            },
            "created_at": now,
        }
    )

    result["events"] = events

    # ------------------------------------------------------------------
    # Progress
    # ------------------------------------------------------------------
    result["progress"] = max(
        float(result.get("progress") or 0.0),
        0.20,
    )

    return result


def run(state: dict[str, Any]) -> dict[str, Any]:
    return investigate(state)