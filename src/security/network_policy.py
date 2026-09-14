"""
Centralized Network Policy Subsystem for Air-Gapped Operation.
Enforces LOCAL_ONLY destination policies and rejects non-loopback host connections.
"""

from enum import Enum
import logging
from urllib.parse import urlparse
from typing import Optional, Set

from config.settings import settings

logger = logging.getLogger("MRPL.Security.NetworkPolicy")


class NetworkMode(str, Enum):
    """Network posture classification mode."""
    LOCAL_ONLY = "LOCAL_ONLY"
    BLOCK_EXTERNAL = "BLOCK_EXTERNAL"
    ALLOW_LOOPBACK = "ALLOW_LOOPBACK"
    ENTERPRISE_LAN = "ENTERPRISE_LAN"


ALLOWED_LOOPBACK_HOSTS: Set[str] = {
    "127.0.0.1",
    "localhost",
    "::1",
    "[::1]",
    "0.0.0.0",
}

BLOCKED_CLOUD_DOMAINS: Set[str] = {
    "api.openai.com",
    "api.anthropic.com",
    "generativelanguage.googleapis.com",
    "huggingface.co",
    "cdn-lfs.huggingface.co",
    "pinecone.io",
    "qdrant.tech",
    "weaviate.network",
    "azure.com",
    "amazonaws.com",
}


class NetworkPolicyError(ValueError):
    """Exception raised when an endpoint URL or host violates air-gapped network policy."""
    pass


class NetworkPolicy:
    """
    Centralized network policy validator enforcing air-gapped local execution rules.
    """

    def __init__(
        self,
        mode: NetworkMode = NetworkMode.LOCAL_ONLY,
        allow_external: Optional[bool] = None,
    ) -> None:
        self.mode = mode
        self.allow_external = allow_external if allow_external is not None else settings.ALLOW_EXTERNAL_NETWORK

    def is_allowed_host(self, host: str) -> bool:
        """
        Check if a hostname or IP address satisfies local network policy.
        """
        if not host:
            return False

        clean_host = host.strip().lower()
        if clean_host.startswith("[") and clean_host.endswith("]"):
            clean_host = clean_host[1:-1]
        elif ":" in clean_host and clean_host.count(":") == 1:
            clean_host = clean_host.split(":")[0]

        # Check loopback hosts
        if clean_host in ALLOWED_LOOPBACK_HOSTS or clean_host.startswith("127."):
            return True

        if not self.allow_external:
            logger.warning(f"[NETWORK POLICY] Blocked non-loopback host: '{clean_host}'")
            return False

        return True

    def validate_host(self, host: str) -> Tuple[bool, str]:
        """Validate host returning (is_allowed, reason) tuple."""
        is_allowed = self.is_allowed_host(host)
        reason = "Host allowed (loopback)" if is_allowed else f"Host '{host}' blocked by LOCAL_ONLY policy"
        return is_allowed, reason


    def is_allowed_url(self, url: str) -> bool:
        """
        Check if a target URL satisfies air-gapped network policy.
        """
        if not url:
            return False

        try:
            parsed = urlparse(url)
            hostname = parsed.hostname or ""

            if not hostname and parsed.netloc:
                hostname = parsed.netloc.split(":")[0]

            if hostname.lower() in BLOCKED_CLOUD_DOMAINS:
                logger.error(f"[NETWORK POLICY] Blocked explicit cloud domain in URL: '{url}'")
                return False

            return self.is_allowed_host(hostname)
        except Exception as exc:
            logger.error(f"[NETWORK POLICY] Failed to parse URL '{url}': {exc}")
            return False

    def validate_url(self, url: str) -> None:
        """
        Validate URL, raising NetworkPolicyError if non-local or prohibited.
        """
        if not self.is_allowed_url(url):
            err_msg = f"Remote endpoint '{url}' rejected by air-gapped network policy (LOCAL_ONLY enforced)."
            logger.error(f"[NETWORK POLICY VIOLATION] {err_msg}")
            raise NetworkPolicyError(err_msg)

    def reject_external_endpoint(self, url: str) -> None:
        """Alias method for validate_url."""
        self.validate_url(url)
