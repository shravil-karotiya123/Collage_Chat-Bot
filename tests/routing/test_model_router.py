"""
Unit tests for ModelRouter execution, telemetry logging, and manager resolution.
"""

from unittest.mock import MagicMock, patch
import pytest

from src.models.deepseek_manager import DeepSeekManager
from src.models.coder_manager import CoderManager
from src.models.qwen_manager import QwenManager
from src.models.vision_manager import VisionManager
from src.routing.base_router import RoutingResult
from src.routing.model_router import ModelRouter
from config.settings import settings


@pytest.fixture
def router() -> ModelRouter:
    return ModelRouter()


def test_route_coding_query(router: ModelRouter) -> None:
    res = router.route("Write a Python function to sort a list of numbers")
    assert isinstance(res, RoutingResult)
    assert isinstance(res.manager, (CoderManager, DeepSeekManager))
    assert res.selected_model == settings.DEFAULT_CODER_MODEL
    assert res.intent == "CODING"
    assert res.status == "SUCCESS"
    assert res.routing_time_ms >= 0.0


def test_route_vision_query(router: ModelRouter) -> None:
    context = {"image_path": "sample.png", "has_image": True}
    res = router.route("What is shown in this image?", context=context)
    assert isinstance(res, RoutingResult)
    assert isinstance(res.manager, VisionManager)
    assert res.selected_model == settings.DEFAULT_VISION_MODEL
    assert res.intent in {"IMAGE", "OCR", "DIAGRAM"}
    assert res.status == "SUCCESS"


def test_route_general_query(router: ModelRouter) -> None:
    res = router.route("Hello, can you explain what MRPL AI Workbench does?")
    assert isinstance(res, RoutingResult)
    assert isinstance(res.manager, QwenManager)
    assert res.selected_model == settings.DEFAULT_QWEN_MODEL
    assert res.intent == "GENERAL_CHAT"
    assert res.status == "SUCCESS"


def test_get_manager_convenience(router: ModelRouter) -> None:
    manager = router.get_manager("Fix bug causing NullPointer exception in Java code")
    assert isinstance(manager, (CoderManager, DeepSeekManager))
    assert manager.model_name == settings.DEFAULT_CODER_MODEL


def test_structured_logging_trigger(router: ModelRouter) -> None:
    with patch("src.routing.model_router.logger.info") as mock_log:
        router.route("Draft an approval note for refinery equipment purchase")
        assert mock_log.called
        log_msg = mock_log.call_args[0][0]
        assert "[MODEL ROUTER]" in log_msg
        assert "APPROVAL_NOTE" in log_msg


def test_router_never_calls_ollama_directly(router: ModelRouter) -> None:
    """Verify that routing operates purely in-memory and does not invoke runtime generate API."""
    with patch("src.models.runtime.ollama_runtime.OllamaRuntime.generate") as mock_generate:
        result = router.route("Write an algorithm in Python")
        assert result.manager is not None
        assert not mock_generate.called
