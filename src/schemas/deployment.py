"""
Deployment Readiness, Backup & Recovery API Pydantic Schemas.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReadinessResponse(BaseModel):
    """Readiness assessment response model for GET /ready."""

    ready: bool = Field(..., description="System production readiness flag")
    status: str = Field(..., description="Readiness summary description")
    timestamp: str = Field(..., description="Assessment ISO timestamp")
    checks: Dict[str, Any] = Field(..., description="Detailed component readiness check results")


class BackupResponse(BaseModel):
    """System backup creation/status payload model."""

    backup_id: str = Field(..., description="Unique backup archive identifier")
    timestamp: str = Field(..., description="Backup completion ISO timestamp")
    destination_path: str = Field(..., description="Absolute file path of backup archive")
    size_bytes: int = Field(..., description="Backup file size in bytes")
    components_included: List[str] = Field(..., description="List of system components archived")
    status: str = Field(default="SUCCESS", description="Backup operation result status")


class RecoveryResponse(BaseModel):
    """Backup restoration result payload model."""

    backup_id: str = Field(..., description="Restored backup archive ID")
    timestamp: str = Field(..., description="Restoration completion ISO timestamp")
    status: str = Field(default="SUCCESS", description="Recovery operation result status")
    components_restored: List[str] = Field(..., description="List of system components restored")
    details: str = Field(..., description="Restoration summary details")
