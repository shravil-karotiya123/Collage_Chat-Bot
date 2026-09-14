"""
Authentication & Authorization API Pydantic Schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Payload for POST /auth/login."""

    username: str = Field(..., description="User login handle", min_length=1)
    password: str = Field(..., description="User secret credential", min_length=1)


class TokenResponse(BaseModel):
    """Token response model for POST /auth/login."""

    access_token: str = Field(..., description="Bearer access token string")
    token_type: str = Field(default="bearer", description="Token type identifier")
    expires_in: int = Field(..., description="Token expiration duration in seconds")
    username: str = Field(..., description="Authenticated user username")
    role: str = Field(..., description="Assigned authorization role")
    permissions: List[str] = Field(default_factory=list, description="Granted permissions list")


class UserResponse(BaseModel):
    """Authenticated user info response model for GET /auth/me."""

    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="User account handle")
    role: str = Field(..., description="User assigned role")
    permissions: List[str] = Field(default_factory=list, description="List of authorized permissions")
    active: bool = Field(default=True, description="Account active status")
