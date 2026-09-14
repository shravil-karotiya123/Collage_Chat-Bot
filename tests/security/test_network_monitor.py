"""
Unit tests for test NetworkMonitor context manager.
"""

import socket
import pytest
from tests.security.network_monitor import NetworkMonitor, NetworkAccessViolation


def test_network_monitor_interception():
    with NetworkMonitor(block_external=True) as monitor:
        # Loopback connection attempt should pass monitor check
        # (socket connect will throw ConnectionRefusedError if no server is listening, but monitor allows it)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            s.connect(("127.0.0.1", 11434))
            s.close()
        except Exception:
            pass

        assert len(monitor.recorded_calls) >= 1
        assert monitor.recorded_calls[0][0] == "127.0.0.1"

        # Non-loopback connection attempt should raise NetworkAccessViolation
        with pytest.raises(NetworkAccessViolation):
            s_ext = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_ext.settimeout(0.1)
            s_ext.connect(("8.8.8.8", 80))
            s_ext.close()
