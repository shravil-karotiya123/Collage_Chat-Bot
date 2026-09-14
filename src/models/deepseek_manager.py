"""
Coder model manager legacy wrapper module.
Maps legacy DeepSeekManager references directly to CoderManager (Qwen2.5-Coder-7B-Instruct).
"""

from typing import Any, Dict, Optional
from src.models.coder_manager import CoderManager


class DeepSeekManager(CoderManager):
    """
    Legacy wrapper delegating to CoderManager (Qwen2.5-Coder-7B-Instruct).
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        runtime: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(model_name=model_name, runtime=runtime, config=config)
