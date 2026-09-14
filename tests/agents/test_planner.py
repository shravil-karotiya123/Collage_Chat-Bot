"""
Unit tests for WorkbenchPlanner intent-driven planning.
"""

from unittest.mock import MagicMock
from src.agents.planner import WorkbenchPlanner
from src.routing.intent_classifier import UserIntent
from src.routing.base_router import RoutingResult


def test_planner_general_chat():
    mock_router = MagicMock()
    mock_router.route.return_value = RoutingResult(
        manager=MagicMock(),
        selected_model="qwen2.5:7b",
        intent="GENERAL_CHAT",
        confidence=1.0,
        routing_time_ms=5.0,
        status="SUCCESS",
        user_query="Hello",
    )

    planner = WorkbenchPlanner(router=mock_router)
    plan = planner.plan(query="Hello")

    assert len(plan.tasks) == 1
    assert plan.tasks[0].tool_name == "chat_tool"
    assert plan.requires_approval is False


def test_planner_document_rag():
    mock_router = MagicMock()
    mock_router.route.return_value = RoutingResult(
        manager=MagicMock(),
        selected_model="qwen2.5:7b",
        intent="DOCUMENT",
        confidence=1.0,
        routing_time_ms=5.0,
        status="SUCCESS",
        user_query="What is in doc?",
    )

    planner = WorkbenchPlanner(router=mock_router)
    plan = planner.plan(query="What is in doc?", document_id="doc_123")

    assert len(plan.tasks) == 2
    assert plan.tasks[0].tool_name == "rag_tool"
    assert plan.tasks[1].tool_name == "chat_tool"
    assert plan.tasks[1].dependencies == [plan.tasks[0].task_id]


def test_planner_approval_note_external_action():
    mock_router = MagicMock()
    mock_router.route.return_value = RoutingResult(
        manager=MagicMock(),
        selected_model="qwen2.5:7b",
        intent="APPROVAL_NOTE",
        confidence=1.0,
        routing_time_ms=5.0,
        status="SUCCESS",
        user_query="Prepare approval note and send to management",
    )

    planner = WorkbenchPlanner(router=mock_router)
    plan = planner.plan(query="Prepare approval note and send to management")

    assert len(plan.tasks) >= 2
    assert plan.requires_approval is True
