"""
Local LLM and Model Server Utilities.

Provides local Ollama connectivity checking, model tag formatting,
and VRAM budget calculation helpers.
"""

from typing import Any, Dict, Optional

from config.settings import settings
from constants.models import SUPPORTED_MODELS, ModelSpec
from utils.logger import logger


def get_model_spec(ollama_tag: str) -> Optional[ModelSpec]:
    """
    Retrieves the ModelSpec dictionary for a given Ollama model tag.

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
    Validates whether a model's VRAM requirements fit within the configured VRAM budget
    (RTX 5050 hardware constraint).

    :param ollama_tag: Target model tag string
    :return: True if required VRAM <= configured MAX_VRAM_USAGE_MB, False otherwise
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
