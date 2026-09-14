"""
Unit tests for TaskStateMachine lifecycle transitions and immutability.
"""

import pytest
from src.agents.agent_types import AgentStatus
from src.agents.state_machine import TaskStateMachine
from src.persistence.exceptions import InvalidTaskStateError


def test_valid_state_transitions():
    assert TaskStateMachine.can_transition(AgentStatus.CREATED, AgentStatus.PLANNING) is True
    assert TaskStateMachine.can_transition(AgentStatus.PLANNING, AgentStatus.WAITING_FOR_APPROVAL) is True
    assert TaskStateMachine.can_transition(AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.APPROVED) is True
    assert TaskStateMachine.can_transition(AgentStatus.APPROVED, AgentStatus.RUNNING) is True
    assert TaskStateMachine.can_transition(AgentStatus.RUNNING, AgentStatus.COMPLETED) is True
    assert TaskStateMachine.can_transition(AgentStatus.RUNNING, AgentStatus.INTERRUPTED) is True
    assert TaskStateMachine.can_transition(AgentStatus.INTERRUPTED, AgentStatus.APPROVED) is True


def test_invalid_state_transitions():
    # Terminal state transition forbidden
    assert TaskStateMachine.can_transition(AgentStatus.COMPLETED, AgentStatus.RUNNING) is False
    assert TaskStateMachine.can_transition(AgentStatus.REJECTED, AgentStatus.RUNNING) is False
    assert TaskStateMachine.can_transition(AgentStatus.CANCELLED, AgentStatus.APPROVED) is False

    with pytest.raises(InvalidTaskStateError):
        TaskStateMachine.validate_transition("task_99", AgentStatus.COMPLETED, AgentStatus.RUNNING)
