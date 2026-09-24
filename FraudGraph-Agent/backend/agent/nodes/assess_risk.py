from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.app.schemas.investigation import InvestigationAssessment, RiskLevel
from backend.ml.inference import FraudModelInference


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _risk_level(score: float) -> RiskLevel:
    if score >= 0.85:
        return RiskLevel.CRITICAL
    if score >= 0.70:
        return RiskLevel.HIGH
    if score >= 0.40:
        return RiskLevel.MEDIUM
    if score >= 0.15:
        return RiskLevel.LOW
    return RiskLevel.UNKNOWN


def _extract_transaction_id(state: dict[str, Any]) -> str | None:
    candidates = (
        state.get("transaction_id"),
        state.get("flagged_txn_id"),
        state.get("transaction", {}).get("TransactionID")
        if isinstance(state.get("transaction"), dict)
        else None,
        state.get("trigger", {}).get("flagged_txn_id")
        if isinstance(state.get("trigger"), dict)
        else None,
        state.get("trigger", {}).get("transaction_id")
        if isinstance(state.get("trigger"), dict)
        else None,
    )

    for value in candidates:
        if value is not None and str(value).strip():
            return str(value).strip()

    return None


def _extract_bank_risk(state: dict[str, Any]) -> float | None:
    candidates = (
        state.get("bank_risk_score"),
        state.get("risk_score"),
        state.get("trigger", {}).get("risk_score")
        if isinstance(state.get("trigger"), dict)
        else None,
        state.get("transaction", {}).get("risk_score")
        if isinstance(state.get("transaction"), dict)
        else None,
    )

    for value in candidates:
        if value is None:
            continue

        try:
            return _clamp(float(value))
        except (TypeError, ValueError):
            continue

    return None


def _extract_pattern_score(state: dict[str, Any]) -> float:
    findings = (
        state.get("pattern_findings")
        or state.get("patterns")
        or state.get("fraud_findings")
        or []
    )

    if not isinstance(findings, list) or not findings:
        return 0.0

    scores: list[float] = []

    for finding in findings:
        if not isinstance(finding, dict):
            continue

        for key in (
            "score",
            "confidence",
            "probability",
            "risk_score",
        ):
            value = finding.get(key)

            if value is None:
                continue

            try:
                scores.append(_clamp(float(value)))
            except (TypeError, ValueError):
                pass

            break

    return max(scores, default=0.0)


def _extract_evidence_score(state: dict[str, Any]) -> float:
    evidence = state.get("evidence") or []

    if not isinstance(evidence, list) or not evidence:
        return 0.0

    scores: list[float] = []

    for item in evidence:
        if not isinstance(item, dict):
            continue

        value = (
            item.get("confidence")
            if item.get("confidence") is not None
            else item.get("score")
        )

        if value is None:
            continue

        try:
            scores.append(_clamp(float(value)))
        except (TypeError, ValueError):
            continue

    if not scores:
        return 0.0

    # Strongest evidence is more useful than a simple average.
    return max(scores)


def _extract_historical_score(state: dict[str, Any]) -> float:
    cases = (
        state.get("related_cases")
        or state.get("similar_cases")
        or state.get("historical_cases")
        or []
    )

    if not isinstance(cases, list) or not cases:
        return 0.0

    scores: list[float] = []

    for case in cases:
        if not isinstance(case, dict):
            continue

        outcome = str(case.get("outcome", "")).lower()

        if outcome in {
            "confirmed_fraud",
            "fraud",
            "confirmed",
        }:
            scores.append(1.0)
            continue

        for key in (
            "similarity",
            "confidence",
            "risk_score",
        ):
            value = case.get(key)

            if value is None:
                continue

            try:
                scores.append(_clamp(float(value)))
            except (TypeError, ValueError):
                pass

            break

    return max(scores, default=0.0)


def _calculate_final_score(
    *,
    ml_probability: float | None,
    bank_risk_score: float | None,
    pattern_score: float,
    evidence_score: float,
    historical_score: float,
) -> float:
    """
    Combine independent investigation signals.

    ML and bank risk are treated as model signals.
    Graph/pattern/evidence/history provide investigation context.

    This is intentionally conservative: a single weak signal should
    not automatically produce a critical investigation risk.
    """

    signals: list[tuple[float, float]] = []

    if ml_probability is not None:
        signals.append((ml_probability, 0.40))

    if bank_risk_score is not None:
        signals.append((bank_risk_score, 0.20))

    if pattern_score > 0:
        signals.append((pattern_score, 0.20))

    if evidence_score > 0:
        signals.append((evidence_score, 0.10))

    if historical_score > 0:
        signals.append((historical_score, 0.10))

    if not signals:
        return 0.0

    weight_total = sum(weight for _, weight in signals)

    return _clamp(
        sum(value * weight for value, weight in signals)
        / weight_total
    )


def _calculate_confidence(
    *,
    ml_probability: float | None,
    bank_risk_score: float | None,
    pattern_score: float,
    evidence_score: float,
    historical_score: float,
) -> float:
    available = [
        value
        for value in (
            ml_probability,
            bank_risk_score,
            pattern_score if pattern_score > 0 else None,
            evidence_score if evidence_score > 0 else None,
            historical_score if historical_score > 0 else None,
        )
        if value is not None
    ]

    if not available:
        return 0.20

    independent_sources = len(available)

    source_confidence = min(
        1.0,
        0.35 + (independent_sources * 0.13),
    )

    # Agreement between model signals increases confidence.
    agreement_bonus = 0.0

    if (
        ml_probability is not None
        and bank_risk_score is not None
    ):
        difference = abs(
            ml_probability - bank_risk_score
        )
        agreement_bonus = max(
            0.0,
            0.15 * (1.0 - difference),
        )

    return _clamp(source_confidence + agreement_bonus)


def _infer_fraud_type(state: dict[str, Any]) -> str | None:
    findings = (
        state.get("pattern_findings")
        or state.get("patterns")
        or []
    )

    if not isinstance(findings, list):
        return None

    names: list[str] = []

    for finding in findings:
        if isinstance(finding, dict):
            value = (
                finding.get("pattern")
                or finding.get("pattern_name")
                or finding.get("name")
                or finding.get("fraud_type")
            )

            if value:
                names.append(str(value))

    if not names:
        return None

    # Preserve the strongest/first detected pattern rather than
    # inventing a classification.
    return names[0]


def _get_model_inference() -> FraudModelInference | None:
    """
    Load the production model from the repository's standard artifact path.

    Failure to load the ML model must not crash the whole investigation;
    graph/pattern/evidence signals can still be evaluated.
    """

    try:
        return FraudModelInference(
            model_path="models/fraud_model.joblib",
            metadata_path="models/fraud_model_metadata.json",
            threshold=0.50,
        )
    except Exception:
        return None


def assess_risk(state: dict[str, Any]) -> dict[str, Any]:
    """
    Assess investigation risk using:
    - bank-provided risk score
    - our trained ML probability
    - fraud patterns
    - collected evidence
    - historical cases

    The original state is preserved and enriched with ML/risk information.
    """

    transaction_id = _extract_transaction_id(state)
    bank_risk_score = _extract_bank_risk(state)

    ml_probability: float | None = None
    ml_prediction: bool | None = None
    model_version: str | None = None
    ml_error: str | None = None

    # ---------------------------------------------------------------
    # ML probability from trigger or real ML inference
    # ---------------------------------------------------------------
    trigger = state.get("trigger") or {}
    if trigger.get("ml_fraud_probability") is not None:
        try:
            ml_probability = float(trigger["ml_fraud_probability"])
            ml_prediction = ml_probability >= 0.50
            model_version = trigger.get("ml_model_version") or "v1.0.0"
        except (TypeError, ValueError):
            pass
    elif transaction_id:
        try:
            from backend.ml.transaction_loader import (
                TransactionRecordLoader,
            )

            loader = TransactionRecordLoader(
                transactions_path="data/raw/transactions.csv",
                identity_path="data/raw/identity.csv",
            )

            transaction = loader.get_transaction(transaction_id)

            if transaction:
                inference = _get_model_inference()

                if inference is not None:
                    prediction = inference.predict(transaction)

                    ml_probability = prediction.probability
                    ml_prediction = prediction.is_fraud
                    model_version = prediction.model_version

        except Exception as exc:
            ml_error = str(exc)

    pattern_score = _extract_pattern_score(state)
    evidence_score = _extract_evidence_score(state)
    historical_score = _extract_historical_score(state)

    final_score = _calculate_final_score(
        ml_probability=ml_probability,
        bank_risk_score=bank_risk_score,
        pattern_score=pattern_score,
        evidence_score=evidence_score,
        historical_score=historical_score,
    )

    confidence = _calculate_confidence(
        ml_probability=ml_probability,
        bank_risk_score=bank_risk_score,
        pattern_score=pattern_score,
        evidence_score=evidence_score,
        historical_score=historical_score,
    )

    uncertainty = _clamp(1.0 - confidence)
    level = _risk_level(final_score)

    fraud_type = _infer_fraud_type(state)

    factors: list[dict[str, Any]] = []

    if bank_risk_score is not None:
        factors.append(
            {
                "source": "bank_model",
                "score": bank_risk_score,
            }
        )

    if ml_probability is not None:
        factors.append(
            {
                "source": "fraud_ml_model",
                "score": ml_probability,
                "prediction": ml_prediction,
                "model_version": model_version,
            }
        )

    if pattern_score > 0:
        factors.append(
            {
                "source": "fraud_patterns",
                "score": pattern_score,
            }
        )

    if evidence_score > 0:
        factors.append(
            {
                "source": "evidence",
                "score": evidence_score,
            }
        )

    if historical_score > 0:
        factors.append(
            {
                "source": "historical_cases",
                "score": historical_score,
            }
        )

    rationale_parts = [
        f"Investigation risk score is {final_score:.3f}.",
        f"Risk level is {level}.",
        f"Confidence is {confidence:.3f}.",
    ]

    if ml_probability is not None:
        rationale_parts.append(
            f"ML fraud probability is {ml_probability:.3f}."
        )

    if bank_risk_score is not None:
        rationale_parts.append(
            f"Bank risk score is {bank_risk_score:.3f}."
        )

    if pattern_score > 0:
        rationale_parts.append(
            f"Detected pattern signal is {pattern_score:.3f}."
        )

    if fraud_type:
        rationale_parts.append(
            f"Primary detected fraud pattern: {fraud_type}."
        )

    if ml_error:
        rationale_parts.append(
            "ML inference was unavailable; remaining investigation "
            "signals were used."
        )

    risk_level_enum = level if isinstance(level, RiskLevel) else RiskLevel(str(level).lower())
    assessment = InvestigationAssessment(
        risk_score=final_score,
        risk_level=risk_level_enum,
        confidence=confidence,
        uncertainty=uncertainty,
        fraud_type=fraud_type,
        rationale=" ".join(rationale_parts),
        bank_risk_score=bank_risk_score,
        ml_fraud_probability=ml_probability,
        ml_used=ml_probability is not None,
        ml_model_version=model_version,
    )

    assessment_dict = {
        "risk_score": final_score,
        "risk_level": risk_level_enum.value,
        "confidence": confidence,
        "uncertainty": uncertainty,
        "fraud_type": fraud_type,
        "rationale": " ".join(rationale_parts),
        "factors": factors,
        "ml_used": ml_probability is not None,
        "ml_fraud_probability": ml_probability,
        "bank_risk_score": bank_risk_score,
    }

    result = dict(state)

    result["bank_risk_score"] = bank_risk_score
    result["ml_fraud_probability"] = ml_probability
    result["ml_prediction"] = ml_prediction
    result["ml_model_version"] = model_version

    if ml_error:
        result["ml_error"] = ml_error

    result["investigation_risk_score"] = final_score
    result["risk_level"] = risk_level_enum
    result["risk_confidence"] = confidence
    result["risk_uncertainty"] = uncertainty
    result["risk_assessment"] = assessment_dict

    # Preserve compatibility with the existing state/result shape.
    result["assessment"] = assessment

    now = _utc_now().isoformat()

    existing_events = list(result.get("events") or [])

    existing_events.append(
        {
            "event_id": f"risk-{transaction_id or 'investigation'}-{now}",
            "event_type": "RISK_ASSESSED",
            "stage": "ASSESS_RISK",
            "message": (
                f"Risk assessed as {level} with score "
                f"{final_score:.3f}."
            ),
            "payload": {
                "transaction_id": transaction_id,
                "bank_risk_score": bank_risk_score,
                "ml_fraud_probability": ml_probability,
                "ml_prediction": ml_prediction,
                "model_version": model_version,
                "pattern_score": pattern_score,
                "evidence_score": evidence_score,
                "historical_score": historical_score,
                "risk_score": final_score,
                "risk_level": level,
                "confidence": confidence,
                "uncertainty": uncertainty,
            },
            "created_at": now,
        }
    )

    result["events"] = existing_events

    return result


# Compatibility aliases for workflows/tests that use different
# naming conventions.
def run(state: dict[str, Any]) -> dict[str, Any]:
    return assess_risk(state)


def assess(state: dict[str, Any]) -> dict[str, Any]:
    return assess_risk(state)
class AssessRiskNode:
    def __init__(self, settings=None):
        self.settings = settings

    def __call__(self, state):
        return assess_risk(state)
    def run(self, state):
        return assess_risk(state)
