"""
FastAPI Router for Agentic Orchestration Subsystem (Phase 10).
Exposes /agent/run, /agent/approve/{task_id}, /agent/reject/{task_id}, /agent/status/{task_id}, /agent/plan/{task_id}, /agent/cancel/{task_id}, /agent/tools, and /agent/health.
Enforces standard response envelopes (StandardResponse[T]).
"""

import time
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_agent_orchestrator
from src.api.responses.standard_response import StandardResponse, success_response
from src.agents.orchestrator import AgentOrchestrator
from src.agents.agent_plan import AgentPlan
from src.schemas.agent import (
    AgentApprovalRequest,
    AgentApprovalResponse,
    AgentHealthResponse,
    AgentPlanResponse,
    AgentRejectionRequest,
    AgentRejectionResponse,
    AgentRunRequest,
    AgentRunResponse,
    AgentStatusResponse,
    AgentTaskSchema,
    AgentToolSchema,
)

from src.auth import (
    require_permission,
    PERMISSION_AGENT_APPROVE,
    PERMISSION_AGENT_REJECT,
    PERMISSION_AGENT_CANCEL,
)

router = APIRouter(prefix="/agent", tags=["Agentic Orchestration"])


@router.post("/run", response_model=StandardResponse[AgentRunResponse])
async def run_agent(
    payload: AgentRunRequest,
    orchestrator: Annotated[AgentOrchestrator, Depends(get_agent_orchestrator)],
) -> StandardResponse[AgentRunResponse]:
    """
    Create and execute an agent task workflow.
    """
    start_time = time.perf_counter()
    state = await orchestrator.run(
        query=payload.query,
        document_id=payload.document_id,
        force_rag=payload.force_rag,
        top_k=payload.top_k,
    )
    exec_time = time.perf_counter() - start_time

    plan_obj = AgentPlan.from_dict(state.plan) if state.plan else None
    plan_id = plan_obj.plan_id if plan_obj else None

    response_data = AgentRunResponse(
        task_id=state.task_id,
        request_id=state.request_id,
        status=state.agent_status.value,
        intent=state.intent,
        selected_model=state.selected_model,
        plan_id=plan_id,
        approval_required=(state.approval_status.value != "NOT_REQUIRED"),
        approval_status=state.approval_status.value,
        final_result=state.final_result,
        task_results=state.task_results,
        execution_time_seconds=round(exec_time, 4),
    )

    msg = "Agent task created and executed successfully" if state.agent_status.value == "COMPLETED" else f"Agent task status: {state.agent_status.value}"
    return success_response(data=response_data, message=msg)


@router.post("/approve/{task_id}", response_model=StandardResponse[AgentApprovalResponse])
async def approve_task(
    task_id: str,
    payload: AgentApprovalRequest,
    orchestrator: Annotated[AgentOrchestrator, Depends(get_agent_orchestrator)],
    user=Depends(require_permission(PERMISSION_AGENT_APPROVE)),
) -> StandardResponse[AgentApprovalResponse]:
    """
    Approve a waiting agent task and trigger execution resumption.
    """
    try:
        approved_state = orchestrator.approve(task_id, comment=payload.comment)
        # Automatically resume execution now that it is approved
        executed_state = await orchestrator.execute(task_id)

        response_data = AgentApprovalResponse(
            task_id=task_id,
            status=executed_state.agent_status.value,
            approval_status=executed_state.approval_status.value,
            message=f"Task approved and executed with status '{executed_state.agent_status.value}'.",
        )
        return success_response(data=response_data, message="Task approved successfully.")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found.")
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))


@router.post("/reject/{task_id}", response_model=StandardResponse[AgentRejectionResponse])
def reject_task(
    task_id: str,
    payload: AgentRejectionRequest,
    orchestrator: Annotated[AgentOrchestrator, Depends(get_agent_orchestrator)],
    user=Depends(require_permission(PERMISSION_AGENT_REJECT)),
) -> StandardResponse[AgentRejectionResponse]:
    """
    Reject a waiting agent task. A rejected task will NEVER execute.
    """
    try:
        rejected_state = orchestrator.reject(task_id, comment=payload.comment)
        response_data = AgentRejectionResponse(
            task_id=task_id,
            status=rejected_state.agent_status.value,
            approval_status=rejected_state.approval_status.value,
            message="Task rejected. Execution halted permanently.",
        )
        return success_response(data=response_data, message="Task rejected successfully.")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found.")


@router.get("/status/{task_id}", response_model=StandardResponse[AgentStatusResponse])
def get_task_status(
    task_id: str,
    orchestrator: Annotated[AgentOrchestrator, Depends(get_agent_orchestrator)],
) -> StandardResponse[AgentStatusResponse]:
    """
    Get progress status of an agent task execution.
    """
    state = orchestrator.get_status(task_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found.")

    tasks_schema = []
    if state.plan:
        plan_obj = AgentPlan.from_dict(state.plan)
        for t in plan_obj.tasks:
            tasks_schema.append(
                AgentTaskSchema(
                    task_id=t.task_id,
                    description=t.description,
                    task_type=t.task_type,
                    tool_name=t.tool_name,
                    dependencies=t.dependencies,
                    status=t.status.value,
                    approval_required=t.approval_required,
                    approval_status=t.approval_status.value,
                    risk_level=t.risk_level.value,
                    result=t.result,
                    error=t.error,
                )
            )

    response_data = AgentStatusResponse(
        task_id=state.task_id,
        request_id=state.request_id,
        status=state.agent_status.value,
        current_step=state.current_step,
        total_steps=state.total_steps,
        approval_status=state.approval_status.value,
        tasks=tasks_schema,
        final_result=state.final_result,
        error=state.error,
    )
    return success_response(data=response_data, message="Task status retrieved successfully.")


@router.get("/plan/{task_id}", response_model=StandardResponse[AgentPlanResponse])
def get_task_plan(
    task_id: str,
    orchestrator: Annotated[AgentOrchestrator, Depends(get_agent_orchestrator)],
) -> StandardResponse[AgentPlanResponse]:
    """
    Get inspectable operational plan for an agent task (redacts internal chain-of-thought).
    """
    state = orchestrator.get_status(task_id)
    if not state or not state.plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan for task '{task_id}' not found.")

    plan_obj = AgentPlan.from_dict(state.plan)
    tasks_schema = [
        AgentTaskSchema(
            task_id=t.task_id,
            description=t.description,
            task_type=t.task_type,
            tool_name=t.tool_name,
            dependencies=t.dependencies,
            status=t.status.value,
            approval_required=t.approval_required,
            approval_status=t.approval_status.value,
            risk_level=t.risk_level.value,
            result=t.result,
            error=t.error,
        )
        for t in plan_obj.tasks
    ]

    response_data = AgentPlanResponse(
        plan_id=plan_obj.plan_id,
        request_id=plan_obj.request_id,
        objective=plan_obj.objective,
        reasoning_summary=plan_obj.reasoning_summary,
        requires_approval=plan_obj.requires_approval,
        tasks=tasks_schema,
        created_at=plan_obj.created_at,
    )
    return success_response(data=response_data, message="Operational plan retrieved successfully.")


@router.post("/cancel/{task_id}", response_model=StandardResponse[AgentStatusResponse])
def cancel_task(
    task_id: str,
    orchestrator: Annotated[AgentOrchestrator, Depends(get_agent_orchestrator)],
    user=Depends(require_permission(PERMISSION_AGENT_CANCEL)),
) -> StandardResponse[AgentStatusResponse]:
    """
    Cancel execution of an active or waiting agent task.
    """
    try:
        cancelled_state = orchestrator.cancel(task_id)
        return get_task_status(task_id, orchestrator)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found.")


@router.get("/tools", response_model=StandardResponse[List[AgentToolSchema]])
def list_tools(
    orchestrator: Annotated[AgentOrchestrator, Depends(get_agent_orchestrator)],
) -> StandardResponse[List[AgentToolSchema]]:
    """
    List all registered agent tools.
    """
    registered_tools = orchestrator.registry.list_tools()
    tools_schema = [
        AgentToolSchema(
            name=t.name,
            description=t.description,
            risk_level=t.risk_level.value,
            requires_approval=t.requires_approval,
            status="healthy",
        )
        for t in registered_tools
    ]
    return success_response(data=tools_schema, message=f"Retrieved {len(tools_schema)} registered tools.")


@router.get("/health", response_model=StandardResponse[AgentHealthResponse])
def agent_health(
    orchestrator: Annotated[AgentOrchestrator, Depends(get_agent_orchestrator)],
) -> StandardResponse[AgentHealthResponse]:
    """
    Get health status of Agentic Orchestration Subsystem.
    """
    h_dict = orchestrator.health()
    response_data = AgentHealthResponse(**h_dict)
    return success_response(data=response_data, message="Agent subsystem is healthy.")
