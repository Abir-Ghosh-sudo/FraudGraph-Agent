from __future__ import annotations

from backend.agent.state import (
    add_error,
    advance_state,
    create_initial_state,
    is_step_limit_reached,
)
from backend.app.schemas.agent import AgentStage
from backend.app.schemas.investigation import InvestigationStatus


def test_create_initial_state():
    state = create_initial_state(
        investigation_id="inv_123",
        trigger={"trigger_type": "fraud_signal", "transaction_id": "txn_001"},
        max_steps=10,
    )
    assert state["investigation_id"] == "inv_123"
    assert state["status"] == InvestigationStatus.PENDING
    assert state["current_stage"] == AgentStage.TRIGGER
    assert state["step"] == 0
    assert state["max_steps"] == 10
    assert state["evidence"] == []


def test_advance_state():
    state = create_initial_state("inv_123", {}, 5)
    updated = advance_state(state, AgentStage.INVESTIGATE, message="Moving to investigate")
    assert updated["current_stage"] == AgentStage.INVESTIGATE
    assert updated["step"] == 1
    assert updated["metadata"]["last_message"] == "Moving to investigate"


def test_add_error_and_step_limit():
    state = create_initial_state("inv_123", {}, 2)
    with_err = add_error(state, "Something went wrong")
    assert "Something went wrong" in with_err["errors"]
    assert not is_step_limit_reached(with_err)

    step1 = advance_state(with_err, AgentStage.INVESTIGATE)
    step2 = advance_state(step1, AgentStage.GATHER_EVIDENCE)
    assert is_step_limit_reached(step2)
