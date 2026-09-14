"""
Real Model Lifecycle and VRAM Eviction Integration Test.
Runs against active local Ollama server when online, skipped when offline.
"""

import os
import pytest

from src.memory.diagnostic import MemoryDiagnostic
from src.memory.memory_manager import MemoryManager
from src.models.model_validator import ModelValidator
from src.models.qwen_manager import QwenManager
from src.models.deepseek_manager import DeepSeekManager
from src.models.vision_manager import VisionManager

validator = ModelValidator()
RUN_REAL = os.environ.get("RUN_REAL_OLLAMA_TESTS") == "1" and validator.check_ollama_server()

pytestmark = pytest.mark.skipif(
    not RUN_REAL,
    reason="RUN_REAL_OLLAMA_TESTS env var not set to 1 or local Ollama server unavailable",
)


def test_real_model_sequential_lifecycle() -> None:
    mem_mgr = MemoryManager()
    diag = MemoryDiagnostic(memory_manager=mem_mgr)

    # 1. Qwen Model Lifecycle
    qwen = QwenManager()
    assert mem_mgr.enforce_single_model_constraint(qwen.model_name) is True
    q_out = qwen.generate("Test prompt for Qwen")
    assert isinstance(q_out, str)
    status_qwen = diag.get_memory_status()
    assert status_qwen["model_lifecycle"]["active_model"] == qwen.model_name

    # 2. DeepSeek Model Lifecycle & Eviction
    deepseek = DeepSeekManager()
    assert mem_mgr.enforce_single_model_constraint(deepseek.model_name) is True
    d_out = deepseek.generate("Write a hello world function in Python")
    assert isinstance(d_out, str)
    status_deepseek = diag.get_memory_status()
    assert status_deepseek["model_lifecycle"]["active_model"] == deepseek.model_name
    # Ensure Qwen is no longer marked as active model
    assert status_deepseek["model_lifecycle"]["active_model"] != qwen.model_name

    # 3. Vision Model Lifecycle & Eviction
    vision = VisionManager()
    assert mem_mgr.enforce_single_model_constraint(vision.model_name) is True
    v_out = vision.generate("Describe engineering diagram")
    assert isinstance(v_out, str)
    status_vision = diag.get_memory_status()
    assert status_vision["model_lifecycle"]["active_model"] == vision.model_name
    # Ensure single model residency
    assert status_vision["model_lifecycle"]["active_model"] != deepseek.model_name
