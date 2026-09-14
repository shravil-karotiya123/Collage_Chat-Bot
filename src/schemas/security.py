"""
Security & Policy Telemetry Pydantic Schemas.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class SecurityStatusResponse(BaseModel):
    """Overall security posture status schema for GET /security/status."""

    status: str = Field(default="healthy", description="Security subsystem operational status")
    authentication_enabled: bool = Field(..., description="Authentication requirement toggle")
    rate_limiting_enabled: bool = Field(..., description="Rate limiting enforcement toggle")
    prompt_injection_detection: bool = Field(..., description="Prompt injection defense toggle")
    blocked_tools_count: int = Field(..., description="Total prohibited tools blocked")
    security_violations_count: int = Field(default=0, description="Total security events recorded")


class SecurityPolicyResponse(BaseModel):
    """Detailed security policy configuration schema for GET /security/policy."""

    authentication_enabled: bool = Field(..., description="Authentication toggle")
    allowed_agent_tools: List[str] = Field(..., description="List of allowlisted agent tools")
    blocked_tools: List[str] = Field(..., description="List of explicitly prohibited tool patterns")
    approval_enabled: bool = Field(..., description="Approval gate enforcement setting")
    rate_limiting_enabled: bool = Field(..., description="Rate limiting toggle")
    max_upload_size_bytes: int = Field(..., description="Maximum document upload threshold")
    prompt_injection_detection_enabled: bool = Field(..., description="Prompt injection defense setting")


class SecurityEventResponse(BaseModel):
    """Security event record model."""

    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Security violation or audit category")
    timestamp: str = Field(..., description="Event ISO timestamp")
    request_id: str = Field(..., description="Associated HTTP request ID")
    actor_id: str = Field(default="system", description="Initiating actor handle")
    severity: str = Field(..., description="Violation severity (LOW, MEDIUM, HIGH, CRITICAL)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event contextual metadata")
