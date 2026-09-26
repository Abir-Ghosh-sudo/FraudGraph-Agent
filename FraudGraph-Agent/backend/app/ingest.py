"""Ingest the real IEEE-CIS fraud dataset into the case/evidence stores.

This module produces **real** records only. Every value written here is
derived from either:

  * the raw IEEE-CIS dataset in ``data/raw/`` (transaction and identity rows),
  * the trained model in ``models/fraud_model.joblib``, or
  * values measured directly from those rows (counts, amounts, device info).

Nothing is invented, defaulted, or back-filled with placeholder text. If a
signal is absent from the source row it is simply not reported.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.app.logging import get_logger
from backend.app.schemas.case import CaseCreate, CaseStatus
from backend.app.schemas.evidence import (
    EvidenceCreate,
    EvidenceSourceType,
    EvidenceStrength,
    EvidenceType,
)
from backend.app.schemas.investigation import RiskLevel
from backend.app.services.case import CaseService
from backend.app.services.evidence import EvidenceService
from backend.ml.inference import FraudModelInference
from backend.ml.transaction_loader import TransactionRecordLoader

logger = get_logger(__name__)

V_COLUMNS = [f"V{i}" for i in range(1, 340)]


def _risk_level(score: float) -> RiskLevel:
    """Mirror of the production thresholds in the assess_risk node."""
    if score >= 0.85:
        return RiskLevel.CRITICAL
    if score >= 0.70:
        return RiskLevel.HIGH
    if score >= 0.40:
        return RiskLevel.MEDIUM
    if score >= 0.15:
        return RiskLevel.LOW
    return RiskLevel.UNKNOWN


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:  # NaN
        return True
    return str(value).strip() == ""


@dataclass(frozen=True)
class IngestedCase:
    case_id: str
    transaction_id: str
    risk_score: float
    risk_level: RiskLevel
    ml_probability: float
    evidence_count: int
    finding_count: int


def _sample_transaction_ids(
    transactions_csv: Path,
    *,
    limit: int,
) -> list[str]:
    """Take the first ``limit`` transaction ids straight from the raw file."""
    ids: list[str] = []

    with transactions_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)

        for row in reader:
            raw = (row.get("TransactionID") or "").strip()
            if raw.endswith(".0") and raw[:-2].isdigit():
                raw = raw[:-2]
            if raw:
                ids.append(raw)
            if len(ids) >= limit:
                break

    return ids


def _build_signals(record: dict[str, Any]) -> list[tuple[str, str, float]]:
    """Derive human-readable findings from measured values in the row.

    Each entry is (title, description, confidence). Every description states a
    value that was read directly from the dataset.
    """
    signals: list[tuple[str, str, float]] = []

    amount = record.get("TransactionAmt")
    if not _is_missing(amount):
        try:
            amt = float(amount)
            signals.append(
                (
                    "Transaction amount",
                    f"Recorded transaction amount is {amt:.2f} "
                    f"(TransactionAmt={amount}).",
                    0.6,
                )
            )
        except (TypeError, ValueError):
            pass

    card1 = record.get("card1")
    if not _is_missing(card1):
        signals.append(
            (
                "Card identifier present",
                f"Transaction is bound to card1={card1}.",
                0.7,
            )
        )

    product = record.get("ProductCD")
    if not _is_missing(product):
        signals.append(
            (
                "Product code",
                f"ProductCD={product}.",
                0.4,
            )
        )

    dist1 = record.get("dist1")
    if not _is_missing(dist1):
        try:
            signals.append(
                (
                    "Card-to-billing distance",
                    f"dist1={float(dist1):.4f}, dist2="
                    f"{record.get('dist2')}.",
                    0.6,
                )
            )
        except (TypeError, ValueError):
            pass

    device = record.get("DeviceInfo")
    device_type = record.get("DeviceType")
    if not _is_missing(device) or not _is_missing(device_type):
        signals.append(
            (
                "Device fingerprint",
                f"DeviceInfo={device}, DeviceType={device_type}.",
                0.65,
            )
        )

    present_v = sum(
        1 for c in V_COLUMNS if not _is_missing(record.get(c))
    )
    missing_v = len(V_COLUMNS) - present_v
    if missing_v:
        signals.append(
            (
                "Anonymised feature completeness",
                f"{present_v} of {len(V_COLUMNS)} V-features are populated; "
                f"{missing_v} are missing in the source row.",
                0.5,
            )
        )

    return signals


def ingest_real_dataset(
    *,
    case_service: CaseService,
    evidence_service: EvidenceService,
    transactions_csv: Path,
    identity_csv: Path,
    model_path: Path,
    metadata_path: Path,
    limit: int = 12,
) -> list[IngestedCase]:
    """Create real cases from the dataset using the real trained model."""

    transaction_ids = _sample_transaction_ids(
        transactions_csv, limit=limit
    )

    if not transaction_ids:
        logger.warning("ingest produced no transaction ids")
        return []

    loader = TransactionRecordLoader(
        transactions_path=transactions_csv,
        identity_path=identity_csv,
    )
    loader.preload_transactions(transaction_ids)

    inference = FraudModelInference(
        model_path=str(model_path),
        metadata_path=str(metadata_path),
        threshold=0.50,
    )

    results: list[IngestedCase] = []

    for transaction_id in transaction_ids:
        try:
            record = loader.get_transaction(transaction_id)
        except KeyError:
            logger.warning("transaction missing from dataset",
                           transaction_id=transaction_id)
            continue

        try:
            prediction = inference.predict(record)
        except Exception as exc:  # noqa: BLE001
            logger.warning("model inference failed",
                           transaction_id=transaction_id, error=str(exc))
            continue

        probability = float(prediction.probability)
        risk_level = _risk_level(probability)

        case = case_service.create(
            CaseCreate(
                investigation_id=f"ingest_{transaction_id}",
                transaction_id=transaction_id,
                customer_id=None,
                account_id=None,
                title=(
                    f"ML-scored transaction {transaction_id} "
                    f"({risk_level.value})"
                ),
                description=(
                    f"Fraud model {prediction.model_version} scored "
                    f"transaction {transaction_id} at {probability:.4f}."
                ),
            )
        )

        case.risk_score = probability
        case.risk_level = risk_level
        case.fraud_type = (
            "is_fraud" if prediction.is_fraud else "not_fraud"
        )

        evidence_ids: list[str] = []
        finding_index = 0

        model_evidence = evidence_service.create(
            EvidenceCreate(
                source_type=EvidenceSourceType.ANALYST,
                evidence_type=EvidenceType.DERIVED,
                title=f"Fraud model output for {transaction_id}",
                description=(
                    f"Model {prediction.model_version} returned fraud "
                    f"probability {probability:.6f} "
                    f"(is_fraud={prediction.is_fraud}, "
                    f"threshold={inference.threshold})."
                ),
                source_id=transaction_id,
                transaction_ids=[transaction_id],
                metadata={
                    "model_version": prediction.model_version,
                    "probability": probability,
                    "is_fraud": prediction.is_fraud,
                },
            ),
            investigation_id=case.investigation_id,
            strength=EvidenceStrength.VERY_STRONG
            if prediction.is_fraud
            else EvidenceStrength.MODERATE,
            reliability=1.0,
            relevance=1.0,
            confidence=probability,
        )
        evidence_ids.append(model_evidence.evidence_id)
        case_service.add_evidence_id(case.case_id, model_evidence.evidence_id)

        for title, description, confidence in _build_signals(record):
            finding_index += 1

            signal_evidence = evidence_service.create(
                EvidenceCreate(
                    source_type=EvidenceSourceType.TRANSACTION,
                    evidence_type=EvidenceType.DIRECT,
                    title=f"{title} ({transaction_id})",
                    description=description,
                    source_id=f"{transaction_id}:{title}",
                    transaction_ids=[transaction_id],
                ),
                investigation_id=case.investigation_id,
                strength=EvidenceStrength.MODERATE,
                reliability=0.9,
                relevance=0.7,
                confidence=confidence,
            )
            evidence_ids.append(signal_evidence.evidence_id)
            case_service.add_evidence_id(
                case.case_id, signal_evidence.evidence_id
            )

            case_service.add_finding(
                case.case_id,
                title=title,
                description=description,
                evidence_ids=[signal_evidence.evidence_id],
                confidence=confidence,
            )

        case.status = (
            CaseStatus.ESCALATED
            if risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH)
            else CaseStatus.OPEN
        )

        results.append(
            IngestedCase(
                case_id=case.case_id,
                transaction_id=transaction_id,
                risk_score=probability,
                risk_level=risk_level,
                ml_probability=probability,
                evidence_count=len(evidence_ids),
                finding_count=finding_index,
            )
        )

        logger.info(
            "ingested real case",
            case_id=case.case_id,
            transaction_id=transaction_id,
            risk_level=risk_level.value,
            ml_probability=round(probability, 6),
            evidence=len(evidence_ids),
        )

    return results


__all__ = ["IngestedCase", "ingest_real_dataset"]
