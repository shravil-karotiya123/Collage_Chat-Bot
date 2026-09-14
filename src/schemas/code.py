"""
Code execution request and response schema models.
"""

from typing import Optional
from pydantic import BaseModel, Field


class CodeExecutionRequest(BaseModel):
    """Code execution request schema."""

    code: str = Field(..., description="Python source code to execute")
    timeout_seconds: int = Field(default=30, description="Execution timeout threshold in seconds")


class CodeExecutionResponse(BaseModel):
    """Code execution response schema."""

    exit_code: int = Field(..., description="Process exit code (0 for clean execution)")
    stdout: str = Field(default="", description="Standard output captured from execution")
    stderr: str = Field(default="", description="Standard error captured from execution")
    execution_time_seconds: float = Field(default=0.0, description="Elapsed execution time")
