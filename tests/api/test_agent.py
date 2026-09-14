"""
API integration unit tests for /agent endpoints.
"""

from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
import pytest

from config.settings import settings
from src.api.app import app
from src.api.dependencies import get_agent_orchestrator
from src.agents.agent_state import AgentState
from src.agents.agent_types import AgentStatus, ApprovalStatus
from src.agents.orchestrator import AgentOrchestrator
from src.agents.tool import BaseTool
from src.agents.tool_registry import ToolRegistry
from src.agents.tool_result import ToolResult
from src.routing.base_router import RoutingResult


class DummyApiTool(BaseTool):
    name = "chat_tool"
    description = "Chat"

    async def execute(self, task_id: str, parameters: dict) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            task_id=task_id,
            data={"answer": "API response payload"},
        )


@pytest.fixture
def client_with_mock_orchestrator():
    mock_router = MagicMock()
    mock_router.route.return_value = RoutingResult(
        manager=MagicMock(),
        selected_model="qwen2.5:7b",
        intent="GENERAL_CHAT",
        confidence=1.0,
        routing_time_ms=5.0,
        status="SUCCESS",
        user_query="Hello API",
    )

    reg = ToolRegistry()
    reg.register(DummyApiTool())

    orch = AgentOrchestrator(router=mock_router, registry=reg)

    app.dependency_overrides[get_agent_orchestrator] = lambda: orch
    client = TestClient(app)
    client.headers["Authorization"] = f"Bearer {settings.AUTH_TOKEN}"
    yield client, orch
    app.dependency_overrides.clear()


def test_agent_health_endpoint(client_with_mock_orchestrator):
    client, _ = client_with_mock_orchestrator
    res = client.get("/agent/health")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["agent_enabled"] is True


def test_agent_tools_endpoint(client_with_mock_orchestrator):
    client, _ = client_with_mock_orchestrator
    res = client.get("/agent/tools")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) >= 1


def test_agent_run_endpoint(client_with_mock_orchestrator):
    client, _ = client_with_mock_orchestrator
    res = client.post("/agent/run", json={"query": "Hello API", "force_rag": False})
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    task_id = json_data["data"]["task_id"]
    assert json_data["data"]["status"] == "COMPLETED"

    # Test status endpoint
    res_status = client.get(f"/agent/status/{task_id}")
    assert res_status.status_code == 200
    assert res_status.json()["data"]["status"] == "COMPLETED"

    # Test plan endpoint
    res_plan = client.get(f"/agent/plan/{task_id}")
    assert res_plan.status_code == 200
    assert res_plan.json()["data"]["plan_id"] is not None


def test_agent_approval_and_rejection_endpoints(client_with_mock_orchestrator):
    client, orch = client_with_mock_orchestrator

    # Override router to trigger approval note with external action
    orch.router.route.return_value = RoutingResult(
        manager=MagicMock(),
        selected_model="qwen2.5:7b",
        intent="APPROVAL_NOTE",
        confidence=1.0,
        routing_time_ms=5.0,
        status="SUCCESS",
        user_query="Draft note and send to management",
    )

    created_state = orch.create_agent_task("Draft note and send to management")
    task_id = created_state.task_id

    # Test reject endpoint
    res_reject = client.post(f"/agent/reject/{task_id}", json={"comment": "Security denial"})
    assert res_reject.status_code == 200
    assert res_reject.json()["data"]["status"] == "REJECTED"

    # Verify task state is now REJECTED
    res_status = client.get(f"/agent/status/{task_id}")
    assert res_status.json()["data"]["status"] == "REJECTED"


def test_agent_nonexistent_task_404(client_with_mock_orchestrator):
    client, _ = client_with_mock_orchestrator
    res = client.get("/agent/status/nonexistent_123")
    assert res.status_code == 404
