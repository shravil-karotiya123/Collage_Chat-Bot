"""
Pydantic Schemas for Persistent Agent State, Durable Job Management, and Recovery.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentTaskCreateRequest(BaseModel):
    """Payload to create a durable agent task."""

    query: str = Field(..., description="Task query or user prompt text", min_length=1)
    session_id: Optional[str] = Field(default="session_default", description="User session identifier")
    document_id: Optional[str] = Field(default=None, description="Optional document ID for RAG context")
    force_rag: Optional[bool] = Field(default=False, description="Require RAG context retrieval")
    top_k: Optional[int] = Field(default=None, description="RAG top_k chunk limit", ge=1, le=20)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional non-sensitive task metadata")


class AgentTaskResponse(BaseModel):
    """Response payload representing durable AgentTask state."""

    task_id: str = Field(..., description="Unique agent task ID")
    user_id: str = Field(..., description="User ID of task owner")
    session_id: str = Field(..., description="Session identifier")
    task_type: str = Field(..., description="Classified task type / intent")
    title: str = Field(..., description="Human-readable task title")
    query: str = Field(..., description="Original user prompt")
    status: str = Field(..., description="Current task status (CREATED, PLANNING, WAITING_FOR_APPROVAL, APPROVED, RUNNING, COMPLETED, FAILED, REJECTED, CANCELLED, INTERRUPTED)")
    risk_level: str = Field(..., description="Evaluated risk level")
    requires_approval: bool = Field(..., description="Flag indicating if governance approval is required")
    approval_status: str = Field(..., description="Current approval status")
    created_at: str = Field(..., description="UTC creation timestamp")
    updated_at: str = Field(..., description="UTC last update timestamp")
    started_at: Optional[str] = Field(default=None, description="UTC execution start timestamp")
    completed_at: Optional[str] = Field(default=None, description="UTC execution completion timestamp")
    cancelled_at: Optional[str] = Field(default=None, description="UTC cancellation timestamp")
    failed_at: Optional[str] = Field(default=None, description="UTC failure timestamp")
    current_step: int = Field(default=0, description="Current step index")
    total_steps: int = Field(default=0, description="Total planned steps")
    retry_count: int = Field(default=0, description="Number of execution retries performed")
    max_retries: int = Field(default=2, description="Maximum allowed retry attempts")
    result_status: str = Field(default="PENDING", description="Result status indicator")
    result_summary: Optional[str] = Field(default=None, description="Safe summary of task result excerpt")
    error_code: Optional[str] = Field(default=None, description="Failure error code if failed")
    error_message: Optional[str] = Field(default=None, description="Failure error message if failed")
    recovery_status: Optional[str] = Field(default=None, description="Recovery status metadata if recovered")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Safe task metadata map")


class AgentTaskListResponse(BaseModel):
    """Paginated list response of durable agent tasks."""

    tasks: List[AgentTaskResponse] = Field(..., description="List of task records")
    total_count: int = Field(..., description="Total tasks matching filter")
    limit: int = Field(..., description="Page limit")
    offset: int = Field(..., description="Page offset")


class AgentExecutionResponse(BaseModel):
    """Response representing an individual tool execution attempt."""

    execution_id: str = Field(..., description="Execution attempt ID")
    task_id: str = Field(..., description="Target task ID")
    step_id: str = Field(..., description="Step identifier")
    attempt_number: int = Field(..., description="Execution attempt index")
    tool_name: str = Field(..., description="Executed tool name")
    status: str = Field(..., description="Execution status")
    started_at: str = Field(..., description="UTC start timestamp")
    completed_at: Optional[str] = Field(default=None, description="UTC completion timestamp")
    duration_ms: float = Field(default=0.0, description="Execution duration in milliseconds")
    safe_input_metadata: Dict[str, Any] = Field(default_factory=dict, description="Safe input parameter metadata")
    safe_output_metadata: Dict[str, Any] = Field(default_factory=dict, description="Safe output metadata")
    result_excerpt: Optional[str] = Field(default=None, description="Truncated result excerpt")
    error_code: Optional[str] = Field(default=None, description="Execution error code if failed")
    error_message: Optional[str] = Field(default=None, description="Execution error message if failed")


class AgentExecutionListResponse(BaseModel):
    """List response of tool execution attempts for a task."""

    task_id: str = Field(..., description="Task ID")
    executions: List[AgentExecutionResponse] = Field(..., description="Tool execution attempts")


class AgentAuditEventResponse(BaseModel):
    """Response representing a structured audit event."""

    event_id: str = Field(..., description="Audit event ID")
    task_id: str = Field(..., description="Associated task ID")
    timestamp: str = Field(..., description="UTC event timestamp")
    event_type: str = Field(..., description="Audit event type tag")
    actor_id: str = Field(..., description="Actor user/system ID")
    actor_role: str = Field(..., description="Actor RBAC role")
    component: str = Field(..., description="Subsystem component emitting event")
    status: str = Field(..., description="Event status")
    tool_name: Optional[str] = Field(default=None, description="Target tool name if applicable")
    risk_level: Optional[str] = Field(default=None, description="Evaluated risk level")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Safe event metadata map")
    correlation_id: Optional[str] = Field(default=None, description="Request correlation ID")


class AgentAuditResponse(BaseModel):
    """Paginated list response of audit events for a task."""

    task_id: str = Field(..., description="Task ID")
    events: List[AgentAuditEventResponse] = Field(..., description="Audit log trajectory events")
    total_count: int = Field(..., description="Total events for task")
    limit: int = Field(..., description="Page limit")
    offset: int = Field(..., description="Page offset")


class TimelineEventItem(BaseModel):
    """Item representing a single lifecycle event on task timeline."""

    event: str = Field(..., description="Event type tag")
    timestamp: str = Field(..., description="UTC event timestamp")
    actor_id: str = Field(default="system", description="Actor identity")
    status: str = Field(default="SUCCESS", description="Event status")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event summary metadata")


class AgentTimelineResponse(BaseModel):
    """Chronological lifecycle timeline of an agent task."""

    task_id: str = Field(..., description="Task ID")
    timeline: List[TimelineEventItem] = Field(..., description="Ordered list of timeline events")


class AgentResumeRequest(BaseModel):
    """Request payload to explicitly resume an INTERRUPTED task."""

    comment: Optional[str] = Field(default="Resumed by operator", description="Resume action comment")


class AgentRetryRequest(BaseModel):
    """Request payload to retry a FAILED task."""

    reason: Optional[str] = Field(default="Retried by operator", description="Retry request reason")


class AgentRecoveryResponse(BaseModel):
    """Response payload for startup recovery and task resume operations."""

    status: str = Field(..., description="Recovery status tag")
    message: str = Field(..., description="Summary message")
    task_id: Optional[str] = Field(default=None, description="Task ID if resuming specific task")
    previous_status: Optional[str] = Field(default=None, description="Previous task status")
    new_status: Optional[str] = Field(default=None, description="New task status")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional recovery metadata")


class PersistenceHealthResponse(BaseModel):
    """Persistence telemetry status response."""

    enabled: bool = Field(..., description="Flag indicating if persistence is active")
    provider: str = Field(default="SQLite", description="Storage provider tag")
    status: str = Field(..., description="Health status indicator")
    database_name: str = Field(..., description="Sanitized database file name")
    database_size_mb: float = Field(..., description="Database size in MB")
    schema_version: int = Field(..., description="Active schema version")
    tasks_total: int = Field(..., description="Total recorded tasks count")
    tasks_running: int = Field(..., description="Active running tasks count")
    tasks_waiting_for_approval: int = Field(..., description="Tasks waiting for approval count")
    tasks_completed: int = Field(..., description="Completed tasks count")
    tasks_failed: int = Field(..., description="Failed tasks count")
    tasks_interrupted: int = Field(..., description="Interrupted tasks count")


class PersistenceBackupResponse(BaseModel):
    """Response payload for database snapshot backup creation."""

    status: str = Field(..., description="Backup status tag")
    filename: str = Field(..., description="Backup filename")
    backup_path: str = Field(..., description="Backup file destination path")
    file_size_mb: float = Field(..., description="Backup file size in MB")
    created_at: str = Field(..., description="UTC creation timestamp")
