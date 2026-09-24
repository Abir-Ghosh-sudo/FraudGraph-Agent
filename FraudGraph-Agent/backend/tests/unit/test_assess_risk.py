from __future__ import annotations

from backend.agent.nodes.assess_risk import AssessRiskNode
from backend.agent.state import create_initial_state
from backend.app.config import Settings
from backend.app.schemas.investigation import RiskLevel


def test_assess_risk_fallback_when_no_ml():
    settings = Settings()
    node = AssessRiskNode(settings)
    state = create_initial_state(
        "inv_test_1",
        {"trigger_type": "customer_report", "risk_score": 0.45},
        max_steps=10,
    )
    result = node(state)
    assessment = result["assessment"]
    assert assessment.risk_score is not None
    assert assessment.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert assessment.ml_used is False
    assert assessment.ml_fraud_probability is None
    assert assessment.bank_risk_score == 0.45


def test_assess_risk_with_ml_probability_in_trigger():
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
    assert assessment.ml_fraud_probability == 0.95
    assert assessment.ml_model_version == "v1.0.0"
    assert assessment.bank_risk_score == 0.80
    assert assessment.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]


def test_assess_risk_with_real_transaction():
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
    assert assessment.bank_risk_score == 0.61
    assert assessment.ml_model_version == "v1.0.0"
