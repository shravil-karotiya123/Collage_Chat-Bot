"""
MRPL AI Workbench — Network Policy Module
Defines NetworkTrustProfile enum and sovereignty constraints.
"""

from enum import Enum
from typing import Dict, Any


class NetworkTrustProfile(str, Enum):
    """
    Network Sovereignty Trust Profiles.
    """
    STRICT_AIRGAP = "STRICT_AIRGAP"
    INDUSTRIAL_LAN = "INDUSTRIAL_LAN"
    DEVELOPMENT = "DEVELOPMENT"


class NetworkPolicy:
    """
    Policy engine determining permitted socket connections based on profile.
    """

    def __init__(self, profile: NetworkTrustProfile = NetworkTrustProfile.STRICT_AIRGAP) -> None:
        self.profile = profile

    def is_host_allowed(self, host: str) -> bool:
        """
        Check if host destination is allowed under current trust profile.
        """
        if self.profile == NetworkTrustProfile.STRICT_AIRGAP:
            # Only loopback addresses allowed
            return host in ("127.0.0.1", "localhost", "::1", "0.0.0.0")
        elif self.profile == NetworkTrustProfile.INDUSTRIAL_LAN:
            # Loopback or local private RFC1918 subnets (10.x, 172.16.x, 192.168.x)
            if host in ("127.0.0.1", "localhost", "::1"):
                return True
            return host.startswith("10.") or host.startswith("192.168.") or host.startswith("172.16.")
        else: # DEVELOPMENT
            return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": self.profile.value,
            "strict_airgap": self.profile == NetworkTrustProfile.STRICT_AIRGAP,
            "allowed_hosts": ["127.0.0.1", "localhost"] if self.profile == NetworkTrustProfile.STRICT_AIRGAP else ["local_subnet"],
        }
