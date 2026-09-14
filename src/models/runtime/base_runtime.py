"""
Abstract base runtime interface definition.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseRuntime(ABC):
    """
    Abstract Base Class defining the interface contract for all local LLM inference engines.
    Conforming runtimes (e.g. Ollama, vLLM, llama.cpp, LM Studio) must implement these methods.
    """

    @abstractmethod
    def load_model(self, model_name: str, **kwargs: Any) -> bool:
        """
        Load a specified model into memory / GPU VRAM.
        """
        pass

    @abstractmethod
    def unload_model(self, model_name: str, **kwargs: Any) -> bool:
        """
        Unload a specified model from memory / GPU VRAM.
        """
        pass

    @abstractmethod
    def generate(self, prompt: str, model_name: str, **kwargs: Any) -> str:
        """
        Generate text response for a prompt using the target local model.
        """
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Query runtime health and system telemetry.
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List all locally available models installed on the inference engine.
        """
        pass
