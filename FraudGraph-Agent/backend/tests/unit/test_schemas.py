from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.schemas.action import ActionCandidate, ActionType, ApprovalRoute
from backend.app.schemas.evidence import Evidence, EvidenceSourceType, EvidenceStrength, EvidenceType
from backend.app.schemas.investigation import InvestigationTrigger, InvestigationTriggerType, RiskLevel


def test_investigation_trigger_validation():
    trigger = InvestigationTrigger(
        trigger_type=InvestigationTriggerType.FRAUD_SIGNAL,
        transaction_id="txn_123",
        risk_score=0.85,
    )
    assert trigger.trigger_type == InvestigationTriggerType.FRAUD_SIGNAL
    assert trigger.transaction_id == "txn_123"
    assert trigger.risk_score == 0.85

    with pytest.raises(ValidationError):
        # Invalid risk_score > 1.0
        InvestigationTrigger(
            trigger_type=InvestigationTriggerType.FRAUD_SIGNAL,
            risk_score=1.5,
        )


def test_evidence_validation():
    ev = Evidence(
        evidence_id="ev_001",
        evidence_type=EvidenceType.DIRECT,
        source_type=EvidenceSourceType.DEVICE,
        source_id="dev_456",
        title="Suspicious Device",
        description="Device associated with multiple accounts",
        strength=EvidenceStrength.STRONG,
        confidence=0.9,
    )
    assert ev.evidence_id == "ev_001"
    assert ev.confidence == 0.9

    with pytest.raises(ValidationError):
        # Extra fields forbidden
        Evidence(
            evidence_id="ev_002",
            evidence_type=EvidenceType.DIRECT,
            source_type=EvidenceSourceType.DEVICE,
            title="Dev",
            description="Desc",
            unknown_field=True,
        )
