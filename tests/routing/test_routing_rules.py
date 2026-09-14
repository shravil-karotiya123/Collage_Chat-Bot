"""
Unit tests for RoutingRules configuration and mapping resolution.
"""

import pytest
from src.models.coder_manager import CoderManager
from src.models.deepseek_manager import DeepSeekManager
from src.models.qwen_manager import QwenManager
from src.models.vision_manager import VisionManager
from src.routing.intent_classifier import UserIntent
from src.routing.routing_rules import RoutingRules


@pytest.fixture
def rules() -> RoutingRules:
    return RoutingRules(cached_instances=True)


def test_default_intent_mappings(rules: RoutingRules) -> None:
    # General AI (Qwen)
    assert isinstance(rules.get_manager(UserIntent.GENERAL_CHAT), QwenManager)
    assert isinstance(rules.get_manager(UserIntent.DOCUMENT), QwenManager)
    assert isinstance(rules.get_manager(UserIntent.APPROVAL_NOTE), QwenManager)
    assert isinstance(rules.get_manager(UserIntent.SUMMARIZATION), QwenManager)

    # Coding AI (Coder / Qwen2.5-Coder)
    assert isinstance(rules.get_manager(UserIntent.CODING), (CoderManager, DeepSeekManager))
    assert isinstance(rules.get_manager(UserIntent.DEBUGGING), (CoderManager, DeepSeekManager))

    # Vision AI (VisionManager / Qwen2.5-VL)
    assert isinstance(rules.get_manager(UserIntent.IMAGE), VisionManager)
    assert isinstance(rules.get_manager(UserIntent.OCR), VisionManager)
    assert isinstance(rules.get_manager(UserIntent.DIAGRAM), VisionManager)

    # Unknown Fallback
    assert isinstance(rules.get_manager(UserIntent.UNKNOWN), QwenManager)


def test_custom_mapping_override(rules: RoutingRules) -> None:
    rules.set_mapping(UserIntent.GENERAL_CHAT, CoderManager)
    assert isinstance(rules.get_manager(UserIntent.GENERAL_CHAT), CoderManager)

    rules.reset_mappings()
    assert isinstance(rules.get_manager(UserIntent.GENERAL_CHAT), QwenManager)


def test_get_manager_type(rules: RoutingRules) -> None:
    assert rules.get_manager_type(UserIntent.CODING) in {CoderManager, DeepSeekManager}
    assert rules.get_manager_type(UserIntent.IMAGE) == VisionManager
    assert rules.get_manager_type(UserIntent.GENERAL_CHAT) == QwenManager


def test_get_all_mappings(rules: RoutingRules) -> None:
    mappings = rules.get_all_mappings()
    assert mappings["GENERAL_CHAT"] == "QwenManager"
    assert mappings["CODING"] in {"CoderManager", "DeepSeekManager"}
    assert mappings["IMAGE"] == "VisionManager"
