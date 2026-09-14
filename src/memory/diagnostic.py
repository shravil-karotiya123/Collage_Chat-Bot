"""
Memory Diagnostic Utility for MRPL AI Workbench.
Reports system RAM, process memory footprint, GPU VRAM allocation, and active model load state.
Does NOT require a physical GPU for unit testing.
"""

import logging
import os
from typing import Any, Dict, Optional

from config.settings import settings
from src.memory.memory_manager import MemoryManager

logger = logging.getLogger("MRPL.Memory.Diagnostic")


class MemoryDiagnostic:
    """
    Lightweight diagnostic utility providing telemetry on system RAM, process memory,
    GPU/VRAM status, and active LLM load state for 16 GB RAM / RTX 5050 hardware safety.
    """

    def __init__(self, memory_manager: Optional[MemoryManager] = None) -> None:
        self.memory_manager = memory_manager or MemoryManager()

    def get_memory_status(self) -> Dict[str, Any]:
        """
        Collect memory utilization metrics across host system, process, and GPU.

        Returns:
            Dict containing memory telemetry breakdown.
        """
        ram_total_mb = 16384.0  # 16 GB default baseline
        ram_available_mb = 8192.0
        ram_used_pct = 50.0

        try:
            import psutil
            mem = psutil.virtual_memory()
            ram_total_mb = round(mem.total / (1024 * 1024), 2)
            ram_available_mb = round(mem.available / (1024 * 1024), 2)
            ram_used_pct = round(mem.percent, 2)
        except Exception:
            pass

        proc_rss_mb = 0.0
        try:
            import psutil
            proc = psutil.Process(os.getpid())
            proc_rss_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
        except Exception:
            pass

        gpu_available = False
        gpu_device_name = "N/A"
        vram_allocated_mb = 0.0
        vram_total_mb = 0.0

        try:
            import torch
            if torch.cuda.is_available():
                gpu_available = True
                gpu_device_name = torch.cuda.get_device_name(0)
                vram_allocated_mb = round(torch.cuda.memory_allocated(0) / (1024 * 1024), 2)
                vram_total_mb = round(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024), 2)
        except Exception:
            pass

        active_model = (
            getattr(self.memory_manager, "active_model", None)
            or getattr(self.memory_manager.gpu_manager, "currently_loaded_model", None)
            or "None (VRAM clear)"
        )
        mem_health = self.memory_manager.get_system_memory_status()

        return {
            "status": "healthy",
            "system_ram": {
                "total_mb": ram_total_mb,
                "available_mb": ram_available_mb,
                "used_pct": ram_used_pct,
            },
            "process_memory": {
                "rss_mb": proc_rss_mb,
            },
            "gpu": {
                "available": gpu_available,
                "device_name": gpu_device_name,
                "vram_allocated_mb": vram_allocated_mb,
                "vram_total_mb": vram_total_mb,
            },
            "model_lifecycle": {
                "active_model": active_model,
                "single_model_enforced": True,
                "memory_health": mem_health,
            },
            "safety_recommendation": (
                "VRAM usage optimal" if vram_allocated_mb < 6144 else "High VRAM load - evict idle models"
            ),
        }


def get_memory_diagnostic() -> MemoryDiagnostic:
    """Factory helper returning MemoryDiagnostic instance."""
    return MemoryDiagnostic()
