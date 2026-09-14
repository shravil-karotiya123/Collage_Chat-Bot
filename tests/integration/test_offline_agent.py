"""
Integration tests for AgentPolicy offline boundary enforcement.
"""

from src.agents.policies import AgentPolicy, PROHIBITED_TOOL_NAMES


def test_agent_offline_policy_boundaries():
    policy = AgentPolicy()

    # Verify all remote and network tools are prohibited
    assert policy.is_tool_allowed("network_tool") is False
    assert policy.is_tool_allowed("external_api_tool") is False
    assert policy.is_tool_allowed("remote_http") is False
    assert policy.is_tool_allowed("cloud_llm") is False
    assert policy.is_tool_allowed("cloud_embedding") is False
    assert policy.is_tool_allowed("cloud_vector_store") is False
    assert policy.is_tool_allowed("external_ocr") is False

    # Allowed tools
    assert policy.is_tool_allowed("rag_tool") is True
    assert policy.is_tool_allowed("document_tool") is True
    assert policy.is_tool_allowed("vision_tool") is True
    assert policy.is_tool_allowed("coding_tool") is True
    assert policy.is_tool_allowed("chat_tool") is True
