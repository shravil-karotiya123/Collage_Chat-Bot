"""
Agent Orchestrator Central Coordinator Module.
Coordinates Model Routing, Deterministic Planning, Policy Enforcement, Approval Gates, Task Execution, and Audit Logging.
"""

from datetime import datetime, timezone
import logging
import time
import uuid
from typing import Any, Dict, Optional

from config.settings import settings
from src.agents.agent_plan import AgentPlan
from src.agents.agent_state import AgentState
from src.agents.agent_types import AgentStatus, ApprovalStatus, TaskStatus
from src.agents.approval_gate import ApprovalGate
from src.agents.audit import AgentAuditLogger
from src.agents.executor import AgentExecutor
from src.agents.planner import BasePlanner, WorkbenchPlanner
from src.agents.policies import AgentPolicy
from src.agents.state_store import AgentStateStore, InMemoryAgentStateStore
from src.agents.tool_registry import ToolRegistry
from src.agents.tools.chat_tool import ChatTool
from src.agents.tools.coding_tool import CodingTool
from src.agents.tools.document_tool import DocumentTool
from src.agents.tools.rag_tool import RAGTool
from src.agents.tools.vision_tool import VisionTool
from src.routing.base_router import BaseRouter
from src.routing.router_factory import RouterFactory

logger = logging.getLogger("MRPL.Agents.Orchestrator")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AgentOrchestrator:
    """
    Central Orchestrator managing end-to-end agentic workflow lifecycle.
    """

    def __init__(
        self,
        router: Optional[BaseRouter] = None,
        planner: Optional[BasePlanner] = None,
        registry: Optional[ToolRegistry] = None,
        state_store: Optional[AgentStateStore] = None,
        policy: Optional[AgentPolicy] = None,
        approval_gate: Optional[ApprovalGate] = None,
        audit_logger: Optional[AgentAuditLogger] = None,
    ) -> None:
        self.router = router or RouterFactory.create_router()
        self.planner = planner or WorkbenchPlanner(router=self.router)
        self.registry = registry or self._build_default_registry()
        self.state_store = state_store or InMemoryAgentStateStore()
        self.policy = policy or AgentPolicy()
        self.approval_gate = approval_gate or ApprovalGate(policy=self.policy)
        self.audit_logger = audit_logger or AgentAuditLogger()

        self.executor = AgentExecutor(
            tool_registry=self.registry,
            policy=self.policy,
            approval_gate=self.approval_gate,
            audit_logger=self.audit_logger,
        )

    def _build_default_registry(self) -> ToolRegistry:
        """Initialize standard tool registry with system tool adapters."""
        reg = ToolRegistry()
        reg.register(ChatTool(router=self.router))
        reg.register(CodingTool(router=self.router))
        reg.register(DocumentTool())
        reg.register(RAGTool())
        reg.register(VisionTool())
        return reg

    def create_agent_task(
        self,
        query: str,
        document_id: Optional[str] = None,
        force_rag: bool = False,
        top_k: Optional[int] = None,
    ) -> AgentState:
        """
        1. Receive request & Classify Intent
        2. Generate Plan
        3. Evaluate Policy & Approval Gate
        4. Persist State & Plan
        """
        task_id = f"task_{uuid.uuid4().hex[:10]}"
        req_id = f"req_{uuid.uuid4().hex[:10]}"

        # Step 1: Intent Routing
        route_res = self.router.route(query)
        selected_model = route_res.selected_model
        intent_tag = route_res.intent

        # Step 2: Generate Plan
        plan = self.planner.plan(
            query=query,
            document_id=document_id,
            force_rag=force_rag,
            top_k=top_k,
            context={"request_id": req_id},
        )

        # Step 3: Evaluate Approval Gate
        has_approval_req = self.approval_gate.evaluate_plan(plan, self.policy)
        initial_status = AgentStatus.WAITING_FOR_APPROVAL if has_approval_req else AgentStatus.CREATED
        initial_approval = ApprovalStatus.PENDING if has_approval_req else ApprovalStatus.NOT_REQUIRED

        state = AgentState(
            task_id=task_id,
            request_id=req_id,
            user_query=query,
            agent_status=initial_status,
            current_step=0,
            total_steps=len(plan.tasks),
            selected_model=selected_model,
            intent=intent_tag,
            approval_status=initial_approval,
            context={"document_id": document_id, "force_rag": force_rag, "top_k": top_k},
            plan=plan.to_dict(),
        )

        # Step 4: Persist State & Log Event
        self.state_store.save_state(state)
        self.state_store.save_plan(plan)

        self.audit_logger.log_event(
            request_id=req_id,
            task_id=task_id,
            event_type="AGENT_CREATED",
            status=initial_status.value,
            metadata={"intent": intent_tag, "model": selected_model},
        )

        self.audit_logger.log_event(
            request_id=req_id,
            task_id=task_id,
            event_type="PLAN_CREATED",
            status="CREATED",
            metadata={"plan_id": plan.plan_id, "requires_approval": has_approval_req},
        )

        if has_approval_req:
            self.audit_logger.log_event(
                request_id=req_id,
                task_id=task_id,
                event_type="APPROVAL_REQUIRED",
                status="WAITING_FOR_APPROVAL",
            )

        return state

    async def execute(self, task_id: str) -> AgentState:
        """
        Execute an existing agent task by task_id.
        """
        state = self.state_store.get_state(task_id)
        if not state:
            raise KeyError(f"Agent task '{task_id}' not found.")

        # Reconstruct Plan
        if not state.plan:
            raise ValueError(f"No execution plan associated with task '{task_id}'.")

        plan = AgentPlan.from_dict(state.plan)

        # Enforce safety guard: Rejected tasks must NEVER execute
        if state.agent_status in (AgentStatus.REJECTED, AgentStatus.CANCELLED):
            logger.warning(f"[ORCHESTRATOR] Rejecting execution request for task '{task_id}' in state '{state.agent_status.value}'.")
            return state

        # Enforce safety guard: Unapproved tasks requiring approval must NEVER execute
        if state.agent_status == AgentStatus.WAITING_FOR_APPROVAL and state.approval_status != ApprovalStatus.APPROVED:
            logger.warning(f"[ORCHESTRATOR] Cannot execute task '{task_id}' while waiting for approval.")
            return state

        # Execute Plan via Executor
        updated_state = await self.executor.execute_plan(plan, state)
        self.state_store.save_state(updated_state)
        return updated_state

    async def run(
        self,
        query: str,
        document_id: Optional[str] = None,
        force_rag: bool = False,
        top_k: Optional[int] = None,
    ) -> AgentState:
        """
        Convenience workflow: Create task and execute if no approval is required.
        """
        state = self.create_agent_task(
            query=query,
            document_id=document_id,
            force_rag=force_rag,
            top_k=top_k,
        )

        # If task does not require approval, execute immediately
        if state.agent_status != AgentStatus.WAITING_FOR_APPROVAL:
            return await self.execute(state.task_id)

        return state

    def approve(self, task_id: str, comment: Optional[str] = None) -> AgentState:
        """
        Approve a waiting task so it can proceed to execution (Idempotent).
        """
        state = self.state_store.get_state(task_id)
        if not state:
            raise KeyError(f"Agent task '{task_id}' not found.")

        if state.agent_status == AgentStatus.APPROVED:
            logger.info(f"[ORCHESTRATOR] Task '{task_id}' is already APPROVED (Idempotent call).")
            return state

        if state.agent_status not in (AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.CREATED, AgentStatus.INTERRUPTED):
            raise ValueError(f"Task '{task_id}' is in state '{state.agent_status.value}' and cannot be approved.")

        state.agent_status = AgentStatus.APPROVED
        state.approval_status = ApprovalStatus.APPROVED
        state.metadata["approval_comment"] = comment or "Approved by user/governance."
        state.metadata["approved_at"] = _utc_now_iso()

        # Update tasks in plan to APPROVED
        if state.plan:
            plan = AgentPlan.from_dict(state.plan)
            for t in plan.tasks:
                if t.status in (TaskStatus.WAITING_FOR_APPROVAL, TaskStatus.PENDING) or t.approval_required:
                    t.approval_status = ApprovalStatus.APPROVED
                    t.status = TaskStatus.READY
            state.plan = plan.to_dict()
            self.state_store.save_plan(plan)

        self.state_store.save_state(state)

        self.audit_logger.log_event(
            request_id=state.request_id,
            task_id=task_id,
            event_type="APPROVED",
            status="APPROVED",
            metadata={"comment": comment},
        )

        logger.info(f"[ORCHESTRATOR] Task '{task_id}' APPROVED successfully.")
        return state

    def reject(self, task_id: str, comment: str) -> AgentState:
        """
        Reject a task (Idempotent). Set status to REJECTED. Task will NEVER execute.
        """
        state = self.state_store.get_state(task_id)
        if not state:
            raise KeyError(f"Agent task '{task_id}' not found.")

        if state.agent_status == AgentStatus.REJECTED:
            logger.info(f"[ORCHESTRATOR] Task '{task_id}' is already REJECTED (Idempotent call).")
            return state

        state.agent_status = AgentStatus.REJECTED
        state.approval_status = ApprovalStatus.REJECTED
        state.error = f"Task rejected: {comment}"
        state.metadata["rejection_comment"] = comment
        state.metadata["rejected_at"] = _utc_now_iso()

        # Update tasks in plan to REJECTED
        if state.plan:
            plan = AgentPlan.from_dict(state.plan)
            for t in plan.tasks:
                if t.status in (TaskStatus.WAITING_FOR_APPROVAL, TaskStatus.PENDING, TaskStatus.READY):
                    t.approval_status = ApprovalStatus.REJECTED
                    t.status = TaskStatus.REJECTED
            state.plan = plan.to_dict()
            self.state_store.save_plan(plan)

        self.state_store.save_state(state)

        self.audit_logger.log_event(
            request_id=state.request_id,
            task_id=task_id,
            event_type="REJECTED",
            status="REJECTED",
            metadata={"comment": comment},
        )

        logger.info(f"[ORCHESTRATOR] Task '{task_id}' REJECTED successfully. Execution halted.")
        return state

    def get_status(self, task_id: str) -> Optional[AgentState]:
        """
        Fetch agent task execution state.
        """
        return self.state_store.get_state(task_id)

    def get_plan(self, task_id: str) -> Optional[AgentPlan]:
        """
        Fetch operational execution plan for task.
        """
        state = self.state_store.get_state(task_id)
        if state and state.plan:
            return AgentPlan.from_dict(state.plan)
        return None

    def cancel(self, task_id: str) -> AgentState:
        """
        Cancel active or waiting agent task execution (Idempotent).
        """
        state = self.state_store.get_state(task_id)
        if not state:
            raise KeyError(f"Agent task '{task_id}' not found.")

        if state.agent_status == AgentStatus.CANCELLED:
            logger.info(f"[ORCHESTRATOR] Task '{task_id}' is already CANCELLED (Idempotent call).")
            return state

        state.agent_status = AgentStatus.CANCELLED
        state.metadata["cancelled_at"] = _utc_now_iso()
        self.state_store.save_state(state)

        self.audit_logger.log_event(
            request_id=state.request_id,
            task_id=task_id,
            event_type="AGENT_CANCELLED",
            status="CANCELLED",
        )

        logger.info(f"[ORCHESTRATOR] Task '{task_id}' CANCELLED.")
        return state

    def health(self) -> Dict[str, Any]:
        """
        Agent subsystem health report.
        """
        all_states = self.state_store.list_states()
        active_count = sum(1 for s in all_states if s.agent_status in (AgentStatus.CREATED, AgentStatus.EXECUTING, AgentStatus.PLANNING))
        waiting_approval_count = sum(1 for s in all_states if s.agent_status == AgentStatus.WAITING_FOR_APPROVAL)

        return {
            "agent_enabled": getattr(settings, "AGENT_ENABLED", True),
            "planner_status": "healthy",
            "executor_status": "healthy",
            "registry_status": "healthy",
            "registered_tool_count": len(self.registry.list_tools()),
            "state_store_status": "healthy",
            "audit_status": "healthy" if settings.AGENT_AUDIT_ENABLED else "disabled",
            "policy_status": "active",
            "active_task_count": active_count,
            "approval_queue_count": waiting_approval_count,
        }
