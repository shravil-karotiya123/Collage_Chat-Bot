"""
Unit tests for AgentState serializability and state methods.
"""

from src.agents.agent_state import AgentState
from src.agents.agent_types import AgentStatus, ApprovalStatus


def test_agent_state_initialization_and_serialization():
    state = AgentState(
        task_id="task_123",
        request_id="req_456",
        user_query="Test query",
        selected_model="qwen2.5:7b",
        intent="GENERAL_CHAT",
    )

    assert state.task_id == "task_123"
    assert state.agent_status == AgentStatus.CREATED
    assert state.approval_status == ApprovalStatus.NOT_REQUIRED

    dict_repr = state.to_dict()
    assert dict_repr["task_id"] == "task_123"
    assert dict_repr["agent_status"] == "CREATED"
    assert dict_repr["approval_status"] == "NOT_REQUIRED"

    reconstructed = AgentState.from_dict(dict_repr)
    assert reconstructed.task_id == state.task_id
    assert reconstructed.agent_status == AgentStatus.CREATED
