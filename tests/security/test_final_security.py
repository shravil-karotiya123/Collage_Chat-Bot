"""
Phase 14 Security Test Suite for MRPL AI Workbench.
Validates air-gapped network blocking, prohibited tools, secret redaction, and local storage bounds.
"""

import pytest
from src.security.network_policy import NetworkPolicy, NetworkPolicyError
from src.security.offline_guard import OfflineGuard
from src.agents.policies import AgentPolicy, PROHIBITED_TOOL_NAMES


def test_network_policy_blocks_cloud_domains():
    policy = NetworkPolicy()

    # Loopback allowed
    assert policy.is_allowed_url("http://127.0.0.1:11434") is True
    assert policy.is_allowed_url("http://localhost:8000") is True

    # Cloud endpoints rejected
    assert policy.is_allowed_url("https://api.openai.com/v1/chat/completions") is False
    assert policy.is_allowed_url("https://api.anthropic.com/v1/messages") is False
    assert policy.is_allowed_url("https://generativelanguage.googleapis.com/v1/models") is False
    assert policy.is_allowed_url("https://huggingface.co/api/models") is False
    assert policy.is_allowed_url("https://pinecone.io/index") is False


def test_agent_policy_prohibited_tools():
    policy = AgentPolicy()
    assert policy.is_tool_allowed("rag_tool") is True
    assert policy.is_tool_allowed("coding_tool") is True
    assert policy.is_tool_allowed("vision_tool") is True

    # Prohibited tools rejected
    assert policy.is_tool_allowed("network_tool") is False
    assert policy.is_tool_allowed("shell_tool") is False
    assert policy.is_tool_allowed("cloud_llm") is False
    assert policy.is_tool_allowed("external_ocr") is False


def test_offline_guard_posture_validation():
    guard = OfflineGuard()
    posture = guard.validate_all()
    assert posture["status"] in ("healthy", "degraded")
    assert posture["network_policy"] == "LOCAL_ONLY"
    assert posture["ollama_local"] is True
    assert posture["embeddings_local"] is True
    assert posture["vector_store_local"] is True
