"""
Local LLM and Model Server Utilities.

Provides runtime factory helpers, model validation, and VRAM budget calculation.
"""

from typing import Any, Dict, Optional
from config.settings import settings
from constants.models import SUPPORTED_MODELS, ModelSpec
from src.models.runtime.base_runtime import BaseRuntime
from utils.logger import logger

_GLOBAL_RUNTIME_INSTANCE: Optional[BaseRuntime] = None


def get_runtime(runtime_type: Optional[str] = None) -> BaseRuntime:
    """
    Factory function returning the configured BaseRuntime singleton instance.

    :param runtime_type: Target runtime engine string (e.g., 'ollama'). Defaults to settings.ACTIVE_RUNTIME.
    :return: Instance conforming to BaseRuntime.
    """
    global _GLOBAL_RUNTIME_INSTANCE
    from src.models.runtime.ollama_runtime import OllamaRuntime

    target_runtime = (runtime_type or settings.ACTIVE_RUNTIME).lower()

    if _GLOBAL_RUNTIME_INSTANCE is None:
        if target_runtime == "ollama":
            _GLOBAL_RUNTIME_INSTANCE = OllamaRuntime()
        else:
            logger.warning(f"Unknown runtime type '{target_runtime}'. Falling back to OllamaRuntime.")
            _GLOBAL_RUNTIME_INSTANCE = OllamaRuntime()

    return _GLOBAL_RUNTIME_INSTANCE


def validate_model(model_name: str) -> bool:
    """
    Validates whether a model tag is supported or available on the active runtime.

    :param model_name: Target model tag string (e.g. 'qwen2.5-coder:7b')
    :return: True if valid/available, False otherwise.
    """
    if model_name in SUPPORTED_MODELS:
        return True

    runtime = get_runtime()
    available_models = runtime.list_models()
    return model_name in available_models


def is_loaded(model_name: str) -> bool:
    """
    Checks if a model is currently tracked as loaded in memory/VRAM.

    :param model_name: Target model tag string
    :return: True if loaded, False otherwise
    """
    from src.memory.gpu_manager import GPUManager
    gpu_mgr = GPUManager()
    return gpu_mgr.currently_loaded_model == model_name


def get_model_spec(ollama_tag: str) -> Optional[ModelSpec]:
    """
    Retrieves the ModelSpec dictionary for a given model tag.

    :param ollama_tag: Target model tag (e.g., 'llama3:8b')
    :return: ModelSpec dictionary if supported, None otherwise
    """
    return SUPPORTED_MODELS.get(ollama_tag)


def is_model_supported(ollama_tag: str) -> bool:
    """
    Checks if a model tag is registered in the workbench model catalog.

    :param ollama_tag: Target model tag string
    :return: True if supported, False otherwise
    """
    return ollama_tag in SUPPORTED_MODELS


def check_vram_budget(ollama_tag: str) -> bool:
    """
    Validates whether a model's VRAM requirements fit within the configured VRAM budget.

    :param ollama_tag: Target model tag string
    :return: True if required VRAM <= MAX_VRAM_USAGE_MB, False otherwise
    """
    spec = get_model_spec(ollama_tag)
    if not spec:
        logger.warning(f"Unregistered model '{ollama_tag}'. Cannot verify VRAM budget.")
        return False

    required_vram = spec["vram_required_mb"]
    budget = settings.MAX_VRAM_USAGE_MB
    fits = required_vram <= budget

    if not fits:
        logger.warning(
            f"Model '{ollama_tag}' requires {required_vram} MB VRAM, exceeding budget of {budget} MB."
        )
    return fits
