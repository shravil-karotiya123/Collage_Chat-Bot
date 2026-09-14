"""
Unit tests for NetworkPolicy component.
"""

import pytest
from src.security.network_policy import NetworkPolicy, NetworkPolicyError


def test_network_policy_locality():
    policy = NetworkPolicy(allow_external=False)

    # Allowed loopback destinations
    assert policy.is_allowed_host("127.0.0.1") is True
    assert policy.is_allowed_host("localhost") is True
    assert policy.is_allowed_host("::1") is True

    assert policy.is_allowed_url("http://127.0.0.1:11434") is True
    assert policy.is_allowed_url("http://localhost:8000") is True

    # Forbidden external destinations
    assert policy.is_allowed_host("api.openai.com") is False
    assert policy.is_allowed_host("8.8.8.8") is False

    assert policy.is_allowed_url("https://api.openai.com/v1/chat") is False
    assert policy.is_allowed_url("https://api.anthropic.com/v1/messages") is False

    with pytest.raises(NetworkPolicyError):
        policy.validate_url("https://generativelanguage.googleapis.com")
