"""
Model runtime package initializer.
"""

from src.models.runtime.base_runtime import BaseRuntime
from src.models.runtime.ollama_runtime import OllamaRuntime

__all__ = [
    "BaseRuntime",
    "OllamaRuntime",
]
