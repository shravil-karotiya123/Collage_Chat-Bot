"""
Unit tests for Dependency Injection providers for Phase 13 security.
"""

from src.api.dependencies import get_network_policy, get_offline_guard, get_startup_validator
from src.security.network_policy import NetworkPolicy
from src.security.offline_guard import OfflineGuard
from src.security.startup_validator import StartupValidator


def test_security_dependency_injection():
    pol = get_network_policy()
    assert isinstance(pol, NetworkPolicy)

    guard = get_offline_guard()
    assert isinstance(guard, OfflineGuard)

    val = get_startup_validator()
    assert isinstance(val, StartupValidator)
