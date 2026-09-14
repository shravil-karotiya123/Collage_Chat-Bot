"""
Qwen local model manager specification.
Inherits from BaseModel and delegates runtime execution.
"""

from typing import Any, Dict, Optional
from config.settings import settings
from src.models.base_model import BaseModel
from src.models.runtime.base_runtime import BaseRuntime


class QwenManager(BaseModel):
    """
    Manager abstraction for Qwen local model variants (e.g., Qwen2.5 7B).
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        runtime: Optional[BaseRuntime] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        target_name = model_name or settings.QWEN_MODEL
        super().__init__(model_name=target_name, runtime=runtime, config=config)

    def load(self, **kwargs: Any) -> bool:
        """
        Load Qwen model weights into memory / GPU VRAM via BaseRuntime.
        """
        return super().load(**kwargs)

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Execute Qwen text generation delegating to BaseRuntime.
        """
        return super().generate(prompt=prompt, **kwargs)

    def health(self) -> Dict[str, Any]:
        """
        Query Qwen model health status metrics.
        """
        return super().health()

    def unload(self, **kwargs: Any) -> bool:
        """
        Unload Qwen model weights from memory / GPU VRAM via BaseRuntime.
        """
        return super().unload(**kwargs)

    def get_metadata(self) -> Dict[str, Any]:
        """Retrieve Qwen model architecture metadata."""
        return {
            "model_name": self.model_name,
            "family": "qwen",
            "context_length": 32768,
            "capabilities": ["general_reasoning", "code", "structured_output"],
        }
