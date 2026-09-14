"""
Operator Console Data Aggregation Service.
"""

from typing import Any, Dict, List, Optional

from config.settings import settings
from src.agents.state_store import InMemoryAgentStateStore
from src.observability import get_audit_logger, get_metrics_collector
from src.operator.system_service import SystemService
from src.security import get_security_service


class OperatorService:
    """
    Central data aggregator for Operator APIs and Dashboard.
    """

    def __init__(
        self,
        system_service: Optional[SystemService] = None,
        state_store: Optional[InMemoryAgentStateStore] = None,
    ) -> None:
        self.system_service = system_service or SystemService()
        self.state_store = state_store
        self.metrics_collector = get_metrics_collector()
        self.audit_logger = get_audit_logger()
        self.security_service = get_security_service()

    def get_models_overview(self) -> Dict[str, Any]:
        """Get model catalog telemetry."""
        return {
            "active_model": None,  # Dynamically updated if model loaded
            "configured_models": {
                "qwen": settings.QWEN_MODEL,
                "deepseek": settings.DEFAULT_DEEPSEEK_MODEL,
                "vision": settings.DEFAULT_VISION_MODEL,
                "router": settings.DEFAULT_ROUTER_MODEL,
                "rag": settings.DEFAULT_RAG_MODEL,
            },
            "ollama_status": "reachable",
            "active_runtime": settings.ACTIVE_RUNTIME,
        }

    def get_tasks_summary(self) -> List[Dict[str, Any]]:
        """Retrieve active and recent agent task summaries."""
        if not self.state_store:
            return []

        tasks = []
        for state in self.state_store.list_states():
            tasks.append({
                "task_id": state.task_id,
                "request_id": state.request_id,
                "user_id": getattr(state, "user_id", state.metadata.get("user_id", "operator")),
                "prompt": getattr(state, "prompt", getattr(state, "user_query", "")),
                "agent_status": state.agent_status.value if hasattr(state.agent_status, "value") else str(state.agent_status),
                "intent": state.intent,
                "risk_level": getattr(state, "risk_level", state.metadata.get("risk_level", "LOW")),
                "approval_required": getattr(state, "approval_required", (state.approval_status.value in ("PENDING", "WAITING_FOR_APPROVAL"))),
                "approval_status": state.approval_status.value if hasattr(state.approval_status, "value") else str(state.approval_status),
                "created_at": state.created_at,
                "updated_at": state.updated_at,
            })

        return sorted(tasks, key=lambda t: t["created_at"], reverse=True)
