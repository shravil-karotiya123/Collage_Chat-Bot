"""
Unit tests for AirGapEnforcer and AirGapSentinel network security modules.
"""

import pytest
import tempfile
from pathlib import Path
from src.core.network.network_policy import NetworkPolicy, NetworkTrustProfile
from src.core.network.airgap_enforcer import AirGapEnforcer
from src.core.network.sentinel import AirGapSentinel


def test_airgap_enforcer_strict():
    policy = NetworkPolicy(profile=NetworkTrustProfile.STRICT_AIRGAP)
    enforcer = AirGapEnforcer(policy=policy)

    # Loopback addresses must pass
    assert enforcer.validate_connection("127.0.0.1", 11434) is True
    assert enforcer.validate_connection("localhost", 8000) is True
    assert enforcer.validate_connection("::1", 8000) is True

    # External addresses must raise PermissionError
    with pytest.raises(PermissionError):
        enforcer.validate_connection("api.openai.com", 443)

    with pytest.raises(PermissionError):
        enforcer.validate_connection("8.8.8.8", 53)


def test_airgap_enforcer_industrial_lan():
    policy = NetworkPolicy(profile=NetworkTrustProfile.INDUSTRIAL_LAN)
    enforcer = AirGapEnforcer(policy=policy)

    assert enforcer.validate_connection("10.0.0.5", 8080) is True
    assert enforcer.validate_connection("192.168.1.100", 8080) is True
    assert enforcer.validate_connection("172.16.0.1", 8080) is True

    with pytest.raises(PermissionError):
        enforcer.validate_connection("8.8.8.8", 53)


def test_airgap_enforcer_development():
    policy = NetworkPolicy(profile=NetworkTrustProfile.DEVELOPMENT)
    enforcer = AirGapEnforcer(policy=policy)

    assert enforcer.validate_connection("api.openai.com", 443) is True
    assert enforcer.validate_connection("8.8.8.8", 53) is True


def test_airgap_sentinel_recording():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test_sentinel_log.jsonl"
        sentinel = AirGapSentinel(log_path=log_file)

        obs = sentinel.record_observation("CONNECT", "127.0.0.1", 11434, allowed=True, details="Local Ollama")
        assert obs["event_type"] == "CONNECT"
        assert obs["host"] == "127.0.0.1"
        assert obs["port"] == 11434
        assert obs["allowed"] is True

        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "127.0.0.1" in content
