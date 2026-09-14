"""
Operator Console & System Telemetry API Pydantic Schemas.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OperatorSystemResponse(BaseModel):
    """System diagnostic response schema for GET /operator/system."""

    status: str = Field(default="healthy", description="Overall platform operational status")
    workbench_version: str = Field(..., description="Application software version")
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    environment: str = Field(..., description="Deployment environment mode")
    python_version: str = Field(..., description="Host Python runtime version")
    platform: str = Field(..., description="Host OS platform indicator")


class OperatorModelResponse(BaseModel):
    """Local model catalog diagnostic response schema for GET /operator/models."""

    active_model: Optional[str] = Field(default=None, description="Currently loaded local LLM model tag")
    configured_models: Dict[str, str] = Field(..., description="Configured model roles mapping")
    ollama_status: str = Field(..., description="Local Ollama server health status")
    active_runtime: str = Field(..., description="Active inference engine name")


class OperatorMemoryResponse(BaseModel):
    """VRAM and System RAM diagnostic response schema for GET /operator/memory."""

    vram: Dict[str, Any] = Field(..., description="GPU VRAM telemetry details")
    ram: Dict[str, Any] = Field(..., description="System RAM telemetry details")
    model_lifecycle: Dict[str, Any] = Field(..., description="Model loading lifecycle state")


class OperatorTaskResponse(BaseModel):
    """Agent task summary schema for GET /operator/tasks."""

    task_id: str = Field(..., description="Unique task identifier")
    request_id: str = Field(..., description="Associated request ID")
    user_id: Optional[str] = Field(default="system", description="Task owner user ID")
    prompt: str = Field(..., description="Task input query")
    agent_status: str = Field(..., description="Current agent execution status")
    intent: str = Field(..., description="Detected request intent")
    risk_level: str = Field(..., description="Evaluated risk level")
    approval_required: bool = Field(..., description="Approval requirement indicator")
    approval_status: str = Field(..., description="Human approval gate status")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 last update timestamp")


class AuditEventResponse(BaseModel):
    """Audit telemetry event log entry schema for GET /operator/audit."""

    event_id: str = Field(..., description="Unique audit event ID")
    event_type: str = Field(..., description="Structured audit event classification")
    timestamp: str = Field(..., description="Event ISO timestamp")
    request_id: str = Field(..., description="Associated request ID")
    task_id: Optional[str] = Field(default=None, description="Associated agent task ID")
    actor_id: Optional[str] = Field(default="system", description="Initiating actor or user ID")
    severity: str = Field(default="INFO", description="Event severity classification")
    status: str = Field(..., description="Action outcome status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata details")
