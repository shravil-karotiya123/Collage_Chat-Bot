"""
Qwen2.5-Coder local model manager specification.
Inherits from BaseModel and delegates runtime execution for technical coding tasks.
"""

from typing import Any, Dict, Optional
from config.settings import settings
from src.models.base_model import BaseModel
from src.models.runtime.base_runtime import BaseRuntime


class CoderManager(BaseModel):
    """
    Manager abstraction for Qwen2.5-Coder-7B-Instruct.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        runtime: Optional[BaseRuntime] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        target_name = model_name or getattr(settings, "DEFAULT_CODER_MODEL", "qwen2.5-coder:7b-instruct")
        super().__init__(model_name=target_name, runtime=runtime, config=config)

    def get_metadata(self) -> Dict[str, Any]:
        """Retrieve Coder model architecture metadata."""
        return {
            "model_name": self.model_name,
            "family": "qwen-coder",
            "context_length": 32768,
            "capabilities": ["code_generation", "python_debugging", "sql_generation", "automation_scripts"],
        }
