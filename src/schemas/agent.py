"""
Pydantic Schemas for Agent REST API Endpoints.
Defines request/response models for agent runs, status checks, operational plans, tool listings, and approval workflows.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    """
    Payload for initiating an agent workflow execution.
    """

    query: str = Field(..., description="User query prompt string", min_length=1)
    document_id: Optional[str] = Field(default=None, description="Optional target document ID filter")
    force_rag: bool = Field(default=False, description="Explicit flag requesting RAG context retrieval")
    top_k: int = Field(default=3, description="Number of vector chunks to retrieve for RAG", ge=1, le=20)


# Aliases for backward compatibility in src.schemas package imports
AgentTaskRequest = AgentRunRequest


class AgentRunResponse(BaseModel):
    """
    Outcome payload returned after triggering an agent task run.
    """

    task_id: str = Field(..., description="Unique agent task execution ID")
    request_id: str = Field(..., description="Unique request tracing ID")
    status: str = Field(..., description="Agent workflow lifecycle status")
    intent: str = Field(..., description="Classified request intent")
    selected_model: str = Field(..., description="Primary local model selected by router")
    plan_id: Optional[str] = Field(default=None, description="Generated plan identifier")
    approval_required: bool = Field(default=False, description="Indicator if human approval gate was triggered")
    approval_status: str = Field(..., description="Current approval gate status")
    final_result: Optional[str] = Field(default=None, description="Final synthesized text output or result")
    task_results: List[Dict[str, Any]] = Field(default_factory=list, description="List of individual task tool results")
    execution_time_seconds: float = Field(default=0.0, description="Total execution time in seconds")


AgentTaskResponse = AgentRunResponse



class AgentTaskSchema(BaseModel):
    """
    Representation of an individual task inside an AgentPlan response.
    """

    task_id: str
    description: str
    task_type: str
    tool_name: str
    dependencies: List[str] = Field(default_factory=list)
    status: str
    approval_required: bool
    approval_status: str
    risk_level: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentPlanResponse(BaseModel):
    """
    Inspectable operational plan overview (redacts private internal chain-of-thought).
    """

    plan_id: str
    request_id: str
    objective: str
    reasoning_summary: str = Field(..., description="High-level operational overview string")
    requires_approval: bool
    tasks: List[AgentTaskSchema] = Field(default_factory=list)
    created_at: str


class AgentStatusResponse(BaseModel):
    """
    Detailed progress status of an active or completed agent task.
    """

    task_id: str
    request_id: str
    status: str
    current_step: int
    total_steps: int
    approval_status: str
    tasks: List[AgentTaskSchema] = Field(default_factory=list)
    final_result: Optional[str] = None
    error: Optional[str] = None


class AgentApprovalRequest(BaseModel):
    """
    Request payload for approving a waiting agent task.
    """

    comment: Optional[str] = Field(default=None, description="Optional approval remark/comment")


class AgentApprovalResponse(BaseModel):
    """
    Response payload after approving an agent task.
    """

    task_id: str
    status: str
    approval_status: str
    message: str


class AgentRejectionRequest(BaseModel):
    """
    Request payload for rejecting a waiting agent task.
    """

    comment: str = Field(..., description="Required reason for task rejection", min_length=1)


class AgentRejectionResponse(BaseModel):
    """
    Response payload after rejecting an agent task.
    """

    task_id: str
    status: str
    approval_status: str
    message: str


class AgentToolSchema(BaseModel):
    """
    Inspectable schema detailing a registered tool adapter.
    """

    name: str
    description: str
    risk_level: str
    requires_approval: bool
    status: str = "healthy"


class AgentHealthResponse(BaseModel):
    """
    Health report schema for Agentic Orchestration Subsystem.
    """

    agent_enabled: bool
    planner_status: str
    executor_status: str
    registry_status: str
    registered_tool_count: int
    state_store_status: str
    audit_status: str
    policy_status: str
    active_task_count: int
    approval_queue_count: int
