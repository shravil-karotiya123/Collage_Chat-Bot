"""
Chat request and response schema models.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request payload structure."""

    query: str = Field(..., description="User query prompt text", min_length=1)
    session_id: Optional[str] = Field(default=None, description="Conversation session ID")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature parameter")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual parameters (file paths, image flags)")
    extra_params: Dict[str, Any] = Field(default_factory=dict, description="Additional model parameters")


class ChatResponse(BaseModel):
    """Chat response payload structure."""

    text: str = Field(..., description="Generated text response")
    model_used: str = Field(..., description="Identifier of the local model used")
    intent: Optional[str] = Field(default=None, description="Detected operational intent classification")
    confidence: Optional[float] = Field(default=None, description="Intent classification confidence score")
    routing_time_ms: Optional[float] = Field(default=None, description="Model routing resolution time in milliseconds")
    status: str = Field(default="SUCCESS", description="Execution status indicator")
    tokens_generated: int = Field(default=0, description="Token count in generated response")
    execution_time_seconds: float = Field(default=0.0, description="Inference execution duration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response telemetry metadata")
