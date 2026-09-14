"""
GPU VRAM monitoring and single-model eviction specification.
"""

from typing import Any, Dict, Optional
from config.settings import settings
from utils.logger import logger


class GPUManager:
    """
    Controller tracking VRAM telemetry and active loaded model state across the application.
    """

    _active_model: Optional[str] = None

    def __init__(self, vram_limit_mb: Optional[int] = None) -> None:
        self.vram_limit_mb = vram_limit_mb or settings.MAX_VRAM_USAGE_MB

    @property
    def currently_loaded_model(self) -> Optional[str]:
        """Return currently active loaded model tag."""
        return GPUManager._active_model

    @currently_loaded_model.setter
    def currently_loaded_model(self, model_name: Optional[str]) -> None:
        """Update currently active loaded model tag."""
        GPUManager._active_model = model_name

    def get_vram_usage(self) -> Dict[str, Any]:
        """
        Fetch VRAM budget and currently loaded model state.
        """
        return {
            "vram_limit_mb": self.vram_limit_mb,
            "vram_budget_mb": settings.MAX_VRAM_USAGE_MB,
            "currently_loaded_model": self.currently_loaded_model,
        }

    def unload_active_model(self, runtime: Optional[Any] = None) -> bool:
        """
        Issue unload instruction for currently active model to enforce single-model VRAM loading.
        """
        if self.currently_loaded_model is None:
            return True

        model_to_unload = self.currently_loaded_model
        logger.info(f"GPUManager: Evicting previously loaded model '{model_to_unload}' from VRAM...")

        if runtime is not None:
            runtime.unload_model(model_to_unload)

        self.currently_loaded_model = None
        return True
