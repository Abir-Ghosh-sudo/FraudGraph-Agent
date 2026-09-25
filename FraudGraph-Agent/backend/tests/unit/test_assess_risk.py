from __future__ import annotations

from pathlib import Path

import pytest

from backend.agent.nodes.assess_risk import (
    AssessRiskNode,
    _calculate_confidence,
    _calculate_final_score,
    _clamp,
    _risk_level,
)
from backend.agent.state import create_initial_state
from backend.app.config import Settings
from backend.app.schemas.investigation import RiskLevel

# ---------------------------------------------------------------------------
# Repo-root anchored paths.
#
# Relative paths resolve against the current working directory, so a
# `Path("data/raw/...")` guard silently skips the real-model test whenever
# pytest is invoked from anywhere other than the repository root, while still
# exiting 0. Anchoring to __file__ makes the guard CWD-independent.
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
TRANSACTIONS_CSV = REPO_ROOT / "data" / "raw" / "transactions.csv"
IDENTITY_CSV = REPO_ROOT / "data" / "raw" / "identity.csv"


# ---------------------------------------------------------------------------
# _clamp
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (5.0, 1.0),
        (1.0, 1.0),
        (0.42, 0.42),
        (0.0, 0.0),
        (-3.0, 0.0),
        (-0.0001, 0.0),
    ],
)
def test_clamp_bounds(raw: float, expected: float) -> None:
    assert _clamp(raw) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# _risk_level thresholds
#
# These boundaries drive the enforcement decision, so every branch is pinned
# with the exact score on both sides of each cut-off.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (1.00, RiskLevel.CRITICAL),
        (0.85, RiskLevel.CRITICAL),
        (0.8499, RiskLevel.HIGH),
        (0.70, RiskLevel.HIGH),
        (0.6999, RiskLevel.MEDIUM),
        (0.40, RiskLevel.MEDIUM),
        (0.3999, RiskLevel.LOW),
        (0.15, RiskLevel.LOW),
        (0.1499, RiskLevel.UNKNOWN),
        (0.0, RiskLevel.UNKNOWN),
    ],
)
def test_risk_level_boundaries(score: float, expected: RiskLevel) -> None:
    assert _risk_level(score) is expected


# ---------------------------------------------------------------------------
# _calculate_final_score
# ---------------------------------------------------------------------------
def test_final_score_returns_zero_without_signals() -> None:
    assert (
        _calculate_final_score(
            ml_probability=None,
            bank_risk_score=None,
            pattern_score=0.0,
            evidence_score=0.0,
            historical_score=0.0,
        )
        == 0.0
    )


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        # A single surviving signal keeps its own value: its weight cancels.
        (
            {"ml_probability": 0.9, "bank_risk_score": None},
            0.9,
        ),
        (
            {"ml_probability": None, "bank_risk_score": 0.5},
            0.5,
        ),
        (
            {"ml_probability": None, "pattern_score": 0.8},
            0.8,
        ),
        (
            {"ml_probability": None, "evidence_score": 0.6},
            0.6,
        ),
        (
            {"ml_probability": None, "historical_score": 1.0},
            1.0,
        ),
        # Weighted blend: 0.9*0.40 + 0.5*0.20 + 0.8*0.20 + 0.6*0.10 + 1.0*0.10
        (
            {
                "ml_probability": 0.9,
                "bank_risk_score": 0.5,
                "pattern_score": 0.8,
                "evidence_score": 0.6,
                "historical_score": 1.0,
            },
            0.78,
        ),
    ],
)
def test_final_score_weighting(
    kwargs: dict[str, float | None], expected: float
) -> None:
    score = _calculate_final_score(
        ml_probability=kwargs.get("ml_probability"),
        bank_risk_score=kwargs.get("bank_risk_score"),
        pattern_score=kwargs.get("pattern_score") or 0.0,
        evidence_score=kwargs.get("evidence_score") or 0.0,
        historical_score=kwargs.get("historical_score") or 0.0,
    )
    assert score == pytest.approx(expected)


# ---------------------------------------------------------------------------
# _calculate_confidence
# ---------------------------------------------------------------------------
def test_confidence_floor_without_signals() -> None:
    assert (
        _calculate_confidence(
            ml_probability=None,
            bank_risk_score=None,
            pattern_score=0.0,
            evidence_score=0.0,
            historical_score=0.0,
        )
        == pytest.approx(0.20)
    )


def test_confidence_single_source() -> None:
    assert _calculate_confidence(
        ml_probability=None,
        bank_risk_score=0.5,
        pattern_score=0.0,
        evidence_score=0.0,
        historical_score=0.0,
    ) == pytest.approx(0.35 + 0.13)


def test_confidence_agreement_bonus_applied() -> None:
    # Two model signals that agree receive the full 0.15 bonus.
    assert _calculate_confidence(
        ml_probability=0.95,
        bank_risk_score=0.95,
        pattern_score=0.0,
        evidence_score=0.0,
        historical_score=0.0,
    ) == pytest.approx(0.35 + 2 * 0.13 + 0.15)


def test_confidence_disagreement_reduces_bonus() -> None:
    # |0.9 - 0.5| = 0.4, so the bonus shrinks to 0.15 * 0.6 = 0.09.
    assert _calculate_confidence(
        ml_probability=0.9,
        bank_risk_score=0.5,
        pattern_score=0.0,
        evidence_score=0.0,
        historical_score=0.0,
    ) == pytest.approx(0.35 + 2 * 0.13 + 0.09)


def test_confidence_is_capped_at_one() -> None:
    value = _calculate_confidence(
        ml_probability=0.9,
        bank_risk_score=0.5,
        pattern_score=0.8,
        evidence_score=0.6,
        historical_score=1.0,
    )
    assert value == pytest.approx(1.0)


def test_confidence_is_clamped_at_zero() -> None:
    value = _calculate_confidence(
        ml_probability=0.0,
        bank_risk_score=0.0,
        pattern_score=0.0,
        evidence_score=0.0,
        historical_score=0.0,
    )
    assert value == pytest.approx(0.35 + 2 * 0.13 + 0.15)


# ---------------------------------------------------------------------------
# Node-level behaviour
# ---------------------------------------------------------------------------
def test_assess_risk_fallback_when_no_ml() -> None:
    settings = Settings()
    node = AssessRiskNode(settings)
    state = create_initial_state(
        "inv_test_1",
        {"trigger_type": "customer_report", "risk_score": 0.45},
        max_steps=10,
    )
    result = node(state)
    assessment = result["assessment"]

    assert assessment.ml_used is False
    assert assessment.ml_fraud_probability is None
    assert assessment.bank_risk_score == pytest.approx(0.45)

    # Bank score is the only signal, so it drives the score directly.
    assert assessment.risk_score == pytest.approx(0.45)
    assert assessment.risk_level is RiskLevel.MEDIUM
    assert assessment.confidence == pytest.approx(0.48)
    assert assessment.uncertainty == pytest.approx(0.52)


def test_assess_risk_with_ml_probability_in_trigger() -> None:
    settings = Settings()
    node = AssessRiskNode(settings)
    state = create_initial_state(
        "inv_test_2",
        {
            "trigger_type": "fraud_signal",
            "risk_score": 0.80,
            "ml_fraud_probability": 0.95,
            "ml_model_version": "v1.0.0",
        },
        max_steps=10,
    )
    result = node(state)
    assessment = result["assessment"]

    assert assessment.ml_used is True
    assert assessment.ml_fraud_probability == pytest.approx(0.95)
    assert assessment.ml_model_version == "v1.0.0"
    assert assessment.bank_risk_score == pytest.approx(0.80)

    # Weighted blend of the two model signals: (0.95*0.40 + 0.80*0.20) / 0.60
    assert assessment.risk_score == pytest.approx(0.90)
    assert assessment.risk_level is RiskLevel.CRITICAL
    assert assessment.confidence == pytest.approx(0.7375)


@pytest.mark.parametrize(
    ("raw_risk", "expected_bank", "expected_level"),
    [
        (5.0, 1.0, RiskLevel.CRITICAL),
        (1.5, 1.0, RiskLevel.CRITICAL),
        (-3.0, 0.0, RiskLevel.UNKNOWN),
    ],
)
def test_assess_risk_clamps_out_of_range_bank_score(
    raw_risk: float,
    expected_bank: float,
    expected_level: RiskLevel,
) -> None:
    node = AssessRiskNode(Settings())
    state = create_initial_state(
        "inv_test_clamp",
        {"trigger_type": "customer_report", "risk_score": raw_risk},
        max_steps=10,
    )
    assessment = node(state)["assessment"]

    assert assessment.bank_risk_score == pytest.approx(expected_bank)
    assert assessment.risk_level is expected_level
    assert 0.0 <= assessment.risk_score <= 1.0


def test_assess_risk_ignores_unparsable_bank_score() -> None:
    node = AssessRiskNode(Settings())
    state = create_initial_state(
        "inv_test_garbage",
        {"trigger_type": "customer_report", "risk_score": "not-a-number"},
        max_steps=10,
    )
    assessment = node(state)["assessment"]

    assert assessment.bank_risk_score is None
    assert assessment.risk_score == pytest.approx(0.0)
    assert assessment.risk_level is RiskLevel.UNKNOWN


def test_assess_risk_emits_risk_assessed_event() -> None:
    node = AssessRiskNode(Settings())
    state = create_initial_state(
        "inv_test_event",
        {"trigger_type": "customer_report", "risk_score": 0.45},
        max_steps=10,
    )
    result = node(state)
    events = result.get("events") or []

    assert events, "assess_risk must append an audit event"
    latest = events[-1]
    assert latest["event_type"] == "RISK_ASSESSED"
    assert latest["stage"] == "ASSESS_RISK"
    assert latest["payload"]["risk_score"] == pytest.approx(0.45)


@pytest.mark.skipif(
    not (TRANSACTIONS_CSV.is_file() and IDENTITY_CSV.is_file()),
    reason=(
        "requires the optional raw transaction and identity datasets at "
        f"{REPO_ROOT / 'data' / 'raw'}"
    ),
)
def test_assess_risk_with_real_transaction() -> None:
    settings = Settings()
    node = AssessRiskNode(settings)
    state = create_initial_state(
        "inv_test_3",
        {
            "trigger_type": "risk_score",
            "transaction_id": "3514030",
            "risk_score": 0.61,
        },
        max_steps=10,
    )
    result = node(state)
    assessment = result["assessment"]

    assert assessment.ml_used is True
    assert assessment.ml_fraud_probability is not None
    assert assessment.ml_fraud_probability > 0.90
    assert assessment.bank_risk_score == pytest.approx(0.61)
    assert assessment.ml_model_version == "v1.0.0"

    # Score must stay a valid probability and agree with its own level.
    assert 0.0 <= assessment.risk_score <= 1.0
    assert assessment.risk_level is _risk_level(assessment.risk_score)
