"""
MRPL AI Workbench — Air-Gap Enforcer Module
Intercepts and enforces local network isolation policies.
"""

import logging
import socket
from typing import Optional, Tuple
from src.core.network.network_policy import NetworkPolicy, NetworkTrustProfile

logger = logging.getLogger("MRPL.Core.Network.Enforcer")


class AirGapEnforcer:
    """
    Enforces application-level network egress constraints.
    """

    def __init__(self, policy: Optional[NetworkPolicy] = None) -> None:
        self.policy = policy or NetworkPolicy(profile=NetworkTrustProfile.STRICT_AIRGAP)

    def validate_connection(self, host: str, port: int) -> bool:
        """
        Validate whether a socket connection to target (host, port) is allowed.

        Raises:
            PermissionError: If host violates STRICT_AIRGAP policy.
        """
        if not self.policy.is_host_allowed(host):
            err_msg = f"[AIRGAP ENFORCER REJECT] Outbound connection to '{host}:{port}' blocked by {self.policy.profile.value} policy."
            logger.error(err_msg)
            raise PermissionError(err_msg)
        return True

    def get_status(self) -> dict:
        return self.policy.to_dict()
