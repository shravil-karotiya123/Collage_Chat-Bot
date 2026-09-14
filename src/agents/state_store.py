"""
Agent State Persistence Abstraction Module.
Provides thread-safe state and plan persistence interface, with InMemoryAgentStateStore and SQLiteAgentStateStore implementations.
"""

from abc import ABC, abstractmethod
import threading
from typing import Dict, List, Optional

from src.agents.agent_plan import AgentPlan
from src.agents.agent_state import AgentState
from src.agents.agent_types import AgentStatus, ApprovalStatus
from src.persistence.models import DBPlan, DBTask
from src.persistence.repositories import TaskRepository


class AgentStateStore(ABC):
    """
    Abstract state persistence interface.
    """

    @abstractmethod
    def save_state(self, state: AgentState) -> None:
        pass

    @abstractmethod
    def get_state(self, task_id: str) -> Optional[AgentState]:
        pass

    @abstractmethod
    def delete_state(self, task_id: str) -> bool:
        pass

    @abstractmethod
    def list_states(self) -> List[AgentState]:
        pass

    @abstractmethod
    def save_plan(self, plan: AgentPlan) -> None:
        pass

    @abstractmethod
    def get_plan(self, plan_id: str) -> Optional[AgentPlan]:
        pass


class InMemoryAgentStateStore(AgentStateStore):
    """
    Thread-safe in-memory state store for active agent tasks and plans.
    """

    def __init__(self) -> None:
        self._states: Dict[str, AgentState] = {}
        self._plans: Dict[str, AgentPlan] = {}
        self._lock = threading.Lock()

    def save_state(self, state: AgentState) -> None:
        with self._lock:
            state.touch()
            self._states[state.task_id] = state

    def get_state(self, task_id: str) -> Optional[AgentState]:
        with self._lock:
            return self._states.get(task_id)

    def delete_state(self, task_id: str) -> bool:
        with self._lock:
            if task_id in self._states:
                del self._states[task_id]
                return True
            return False

    def list_states(self) -> List[AgentState]:
        with self._lock:
            return list(self._states.values())

    def save_plan(self, plan: AgentPlan) -> None:
        with self._lock:
            self._plans[plan.plan_id] = plan

    def get_plan(self, plan_id: str) -> Optional[AgentPlan]:
        with self._lock:
            return self._plans.get(plan_id)


class SQLiteAgentStateStore(AgentStateStore):
    """
    Thread-safe SQLite persistent store adapting TaskRepository for durable state management.
    """

    def __init__(self, task_repo: Optional[TaskRepository] = None) -> None:
        self.task_repo = task_repo or TaskRepository()
        self.fallback = InMemoryAgentStateStore()

    def save_state(self, state: AgentState) -> None:
        state.touch()
        self.fallback.save_state(state)

        user_id = state.metadata.get("user_id", "system")
        session_id = state.metadata.get("session_id", "session_default")
        task_type = state.intent or "AGENT_TASK"
        title = state.user_query[:50] if state.user_query else "Agent Task"

        db_task = DBTask(
            task_id=state.task_id,
            user_id=user_id,
            session_id=session_id,
            task_type=task_type,
            title=title,
            query=state.user_query,
            status=state.agent_status.value,
            risk_level=state.metadata.get("risk_level", "LOW"),
            requires_approval=(state.approval_status.value in ("PENDING", "WAITING_FOR_APPROVAL")),
            approval_status=state.approval_status.value,
            created_at=state.created_at,
            updated_at=state.updated_at,
            current_step=state.current_step,
            total_steps=state.total_steps,
            result_status="COMPLETED" if state.final_result else ("FAILED" if state.error else state.agent_status.value),
            result_summary=state.final_result,
            error_message=state.error,
            metadata=state.to_dict(),
        )

        existing = self.task_repo.get_task(state.task_id)
        if existing:
            self.task_repo.update_task(db_task)
        else:
            self.task_repo.create_task(db_task)

    def get_state(self, task_id: str) -> Optional[AgentState]:
        db_task = self.task_repo.get_task(task_id)
        if db_task:
            if db_task.metadata and "agent_status" in db_task.metadata:
                try:
                    return AgentState.from_dict(db_task.metadata)
                except Exception:
                    pass
            # Construct AgentState directly from DBTask record
            try:
                status_enum = AgentStatus(db_task.status) if db_task.status in AgentStatus.__members__ else AgentStatus.CREATED
            except Exception:
                status_enum = AgentStatus.CREATED

            db_plan = self.task_repo.get_plan(task_id)
            plan_dict = None
            if db_plan:
                plan_dict = {
                    "plan_id": db_plan.plan_id,
                    "request_id": db_plan.task_id,
                    "objective": db_task.query,
                    "tasks": db_plan.tasks_graph,
                    "status": db_plan.status,
                    "requires_approval": db_plan.requires_approval,
                    "created_at": db_plan.created_at,
                }
            else:
                from src.agents.agent_task import AgentTask
                plan_dict = {
                    "plan_id": f"plan_{task_id[:8]}",
                    "request_id": task_id,
                    "objective": db_task.query,
                    "tasks": [AgentTask(task_id=f"step_{task_id[:8]}", description=db_task.query, task_type="CHAT", tool_name="chat_tool").to_dict()],
                    "status": status_enum.value,
                    "requires_approval": db_task.requires_approval,
                    "created_at": db_task.created_at,
                }

            try:
                app_status_enum = ApprovalStatus(db_task.approval_status) if db_task.approval_status in ApprovalStatus.__members__ else ApprovalStatus.NOT_REQUIRED
            except Exception:
                app_status_enum = ApprovalStatus.NOT_REQUIRED

            return AgentState(
                task_id=db_task.task_id,
                request_id=db_task.task_id,
                user_query=db_task.query,
                agent_status=status_enum,
                current_step=db_task.current_step,
                total_steps=db_task.total_steps,
                selected_model="qwen2.5:7b",
                intent=db_task.task_type,
                approval_status=app_status_enum,
                plan=plan_dict,
                created_at=db_task.created_at,
                updated_at=db_task.updated_at,
            )
        return self.fallback.get_state(task_id)

    def delete_state(self, task_id: str) -> bool:
        self.fallback.delete_state(task_id)
        return True

    def list_states(self) -> List[AgentState]:
        db_tasks, _ = self.task_repo.list_tasks(limit=100)
        states = []
        for dt in db_tasks:
            if dt.metadata:
                try:
                    states.append(AgentState.from_dict(dt.metadata))
                except Exception:
                    pass
        if not states:
            states = self.fallback.list_states()
        return states

    def save_plan(self, plan: AgentPlan) -> None:
        self.fallback.save_plan(plan)
        target_task_id = getattr(plan, "task_id", None) or plan.request_id
        existing_task = self.task_repo.get_task(target_task_id)
        if not existing_task:
            # Try finding task by request_id or recent task
            db_tasks, _ = self.task_repo.list_tasks(limit=1)
            if db_tasks:
                target_task_id = db_tasks[0].task_id
            else:
                return

        db_plan = DBPlan(
            plan_id=plan.plan_id,
            task_id=target_task_id,
            plan_version=1,
            intent=getattr(plan, "intent", "AGENT_PLAN"),
            selected_model=getattr(plan, "selected_model", "qwen2.5:7b"),
            total_tasks=len(plan.tasks),
            requires_approval=plan.requires_approval,
            status=plan.status.value if hasattr(plan.status, "value") else str(plan.status),
            created_at=plan.created_at,
            tasks_graph=[t.to_dict() for t in plan.tasks],
        )
        try:
            self.task_repo.save_plan(db_plan)
        except Exception:
            pass

    def get_plan(self, plan_id: str) -> Optional[AgentPlan]:
        db_plan = self.task_repo.get_plan(plan_id)
        if db_plan:
            try:
                return AgentPlan.from_dict({
                    "plan_id": db_plan.plan_id,
                    "request_id": db_plan.task_id,
                    "user_query": "",
                    "intent": db_plan.intent,
                    "selected_model": db_plan.selected_model,
                    "status": db_plan.status,
                    "requires_approval": db_plan.requires_approval,
                    "created_at": db_plan.created_at,
                    "tasks": db_plan.tasks_graph,
                })
            except Exception:
                pass
        return self.fallback.get_plan(plan_id)
