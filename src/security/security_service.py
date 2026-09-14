"""
Unified Security & Policy Management Service.
"""

import time
import uuid
from typing import Any, Dict, List, Optional

from config.settings import settings
from src.agents.policies import PROHIBITED_TOOL_NAMES, ALLOWED_SYSTEM_TOOLS
from src.security.input_sanitizer import InputSanitizer
from src.security.rate_limiter import RateLimiter


class SecurityService:
    """
    Unified security management service for rates, policy status, and security telemetry events.
    """

    def __init__(self) -> None:
        self.rate_limiter = RateLimiter(
            requests_limit=settings.RATE_LIMIT_REQUESTS,
            window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
            enabled=settings.RATE_LIMIT_ENABLED,
        )
        self.sanitizer = InputSanitizer(
            enabled=settings.SECURITY_PROMPT_INJECTION_DETECTION
        )
        self._security_events: List[Dict[str, Any]] = []

    def log_security_event(
        self,
        event_type: str,
        request_id: str,
        severity: str = "MEDIUM",
        actor_id: str = "system",
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record structured security violation or audit telemetry event."""
        evt = {
            "event_id": f"sec_{uuid.uuid4().hex[:10]}",
            "event_type": event_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "request_id": request_id,
            "actor_id": actor_id,
            "severity": severity,
            "details": details or {},
        }
        self._security_events.append(evt)
        return evt

    def get_security_status(self) -> Dict[str, Any]:
        """Get summary of security posture and event metrics."""
        return {
            "status": "healthy",
            "offline_mode": settings.OFFLINE_MODE,
            "air_gapped_policy_version": settings.AIR_GAPPED_POLICY_VERSION,
            "authentication_enabled": settings.AUTH_ENABLED,
            "rate_limiting_enabled": settings.RATE_LIMIT_ENABLED,
            "prompt_injection_detection": settings.SECURITY_PROMPT_INJECTION_DETECTION,
            "blocked_tools_count": len(PROHIBITED_TOOL_NAMES),
            "security_violations_count": len(self._security_events),
        }

    def get_security_policy(self) -> Dict[str, Any]:
        """Get complete security policy configuration."""
        return {
            "offline_mode": settings.OFFLINE_MODE,
            "air_gapped_policy_version": settings.AIR_GAPPED_POLICY_VERSION,
            "authentication_enabled": settings.AUTH_ENABLED,
            "allowed_agent_tools": sorted(list(ALLOWED_SYSTEM_TOOLS)),
            "blocked_tools": sorted(list(PROHIBITED_TOOL_NAMES)),
            "approval_enabled": settings.AGENT_REQUIRE_APPROVAL_FOR_HIGH_RISK,
            "rate_limiting_enabled": settings.RATE_LIMIT_ENABLED,
            "max_upload_size_bytes": settings.MAX_DOCUMENT_SIZE_BYTES,
            "prompt_injection_detection_enabled": settings.SECURITY_PROMPT_INJECTION_DETECTION,
        }

    def get_security_events(self) -> List[Dict[str, Any]]:
        """Retrieve recorded security event log entries."""
        return list(self._security_events)
