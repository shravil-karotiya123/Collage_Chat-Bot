"""
Standard API Response Model specification for MRPL AI Workbench.
Enforces consistent JSON envelope structure across all HTTP endpoints.
"""

from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """
    Unified JSON envelope structure for enterprise REST API endpoints.
    """

    success: bool = Field(default=True, description="Operation success indicator")
    status_code: int = Field(default=200, description="HTTP status code")
    message: str = Field(default="Success", description="Human-readable response message")
    data: Optional[T] = Field(default=None, description="Response payload data")
    error: Optional[Any] = Field(default=None, description="Error detail object when success is False")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp of response generation",
    )


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> StandardResponse[Any]:
    """Helper function to build a success StandardResponse wrapper."""
    return StandardResponse(
        success=True,
        status_code=status_code,
        message=message,
        data=data,
        error=None,
    )


def error_response(
    message: str,
    status_code: int = 400,
    error: Any = None,
) -> StandardResponse[Any]:
    """Helper function to build an error StandardResponse wrapper."""
    return StandardResponse(
        success=False,
        status_code=status_code,
        message=message,
        data=None,
        error=error or {"detail": message},
    )
