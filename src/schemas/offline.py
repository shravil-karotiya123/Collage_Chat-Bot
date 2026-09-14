"""
Pydantic Schema Models for Air-Gapped Offline Security Posture & Validation.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OfflineCheckDetail(BaseModel):
    """Result of an individual offline posture verification check."""

    name: str = Field(..., description="Validation check identifier name")
    status: str = Field(..., description="Check status (PASS, WARNING, FAIL)")
    details: str = Field(..., description="Human-readable verification detail")


class OfflineStatusResponse(BaseModel):
    """Response payload for GET /security/offline endpoint."""

    status: str = Field(..., description="Overall offline posture status (healthy, degraded, unhealthy)")
    offline_mode: bool = Field(default=True, description="Flag indicating if offline execution mode is active")
    strict_mode: bool = Field(default=True, description="Flag indicating if strict air-gapped policy is enforced")
    network_policy: str = Field(default="LOCAL_ONLY", description="Active network policy mode")
    ollama_local: bool = Field(default=True, description="Flag indicating Ollama runtime endpoint is local")
    cloud_disabled: bool = Field(default=False, description="Flag indicating if Ollama cloud functionality is disabled")
    models_local: bool = Field(default=True, description="Flag indicating all production models are installed locally")
    embeddings_local: bool = Field(default=True, description="Flag indicating embedding provider uses local model files")
    vector_store_local: bool = Field(default=True, description="Flag indicating ChromaDB vector store is local")
    ocr_local: bool = Field(default=True, description="Flag indicating OCR engines are local")
    persistence_local: bool = Field(default=True, description="Flag indicating SQLite persistence is local")
    policy_violations: List[str] = Field(default_factory=list, description="List of recorded security policy violations")
    external_dependencies_detected: int = Field(default=0, description="Count of non-local external dependencies detected")


class OfflineValidationResponse(BaseModel):
    """Response payload for POST /security/offline/validate endpoint."""

    status: str = Field(..., description="Validation summary status")
    validation_scope: str = Field(default="configuration", description="Validation scope (configuration or network_disconnected)")
    checks: List[OfflineCheckDetail] = Field(..., description="Detailed verification check items")
