"""
Test-only Network Call Interceptor & Monitor.
Monkeypatches socket creation during automated test runs to detect and block accidental external network calls.
"""

import socket
import logging
from typing import List, Tuple, Union, Any

logger = logging.getLogger("MRPL.Tests.NetworkMonitor")

ALLOWED_TEST_HOSTS = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}


class NetworkAccessViolation(RuntimeError):
    """Exception raised when an automated test attempts an external network call."""
    pass


class NetworkMonitor:
    """
    Context manager intercepting socket connection attempts during tests.
    """

    def __init__(self, block_external: bool = True) -> None:
        self.block_external = block_external
        self.recorded_calls: List[Tuple[str, int]] = []
        self._original_connect = None

    def __enter__(self) -> "NetworkMonitor":
        self._original_connect = socket.socket.connect

        def guarded_connect(sock_obj: socket.socket, address: Union[Tuple[Any, ...], str]) -> Any:
            host = ""
            port = 0
            if isinstance(address, tuple) and len(address) >= 2:
                host = str(address[0])
                port = int(address[1])
            elif isinstance(address, str):
                host = address

            self.recorded_calls.append((host, port))

            if host not in ALLOWED_TEST_HOSTS and not host.startswith("127."):
                logger.error(f"[NETWORK MONITOR VIOLATION] Test attempted external connection to: {host}:{port}")
                if self.block_external:
                    raise NetworkAccessViolation(
                        f"External network call to '{host}:{port}' blocked by test NetworkMonitor."
                    )

            return self._original_connect(sock_obj, address)

        socket.socket.connect = guarded_connect  # type: ignore
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._original_connect:
            socket.socket.connect = self._original_connect  # type: ignore
