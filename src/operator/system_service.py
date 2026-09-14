"""
System Telemetry & Hardware Resource Diagnostic Provider.
"""

import os
import platform
import sys
import time
from typing import Any, Dict

from config.settings import settings
from src.memory.diagnostic import MemoryDiagnostic


class SystemService:
    """
    Host system diagnostic provider.
    Correctly distinguishes physical GPU hardware telemetry from configured VRAM budget limits.
    """

    def __init__(self) -> None:
        self.start_time = time.time()
        self.memory_diag = MemoryDiagnostic()

    def get_system_status(self) -> Dict[str, Any]:
        """Get host system operational status metrics."""
        uptime = round(time.time() - self.start_time, 2)
        return {
            "status": "healthy",
            "workbench_version": settings.WORKBENCH_VERSION,
            "uptime_seconds": uptime,
            "environment": settings.ENVIRONMENT,
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        }

    def get_memory_diagnostics(self) -> Dict[str, Any]:
        """Get RAM, VRAM, and model lifecycle telemetry."""
        diag = self.memory_diag.get_memory_status()
        sys_ram = diag.get("system_ram", {})
        gpu_info = diag.get("gpu", {})

        vram_info = {
            "available": gpu_info.get("available", False),
            "device_name": gpu_info.get("device_name", "N/A"),
            "allocated_vram_mb": gpu_info.get("vram_allocated_mb", 0.0),
            "total_vram_mb": gpu_info.get("vram_total_mb", 0.0),
            "configured_budget_mb": settings.MAX_VRAM_USAGE_MB,
        }

        ram_info = {
            "total_ram_mb": sys_ram.get("total_mb", 16384.0),
            "available_ram_mb": sys_ram.get("available_mb", 8192.0),
            "used_ram_mb": round(sys_ram.get("total_mb", 16384.0) - sys_ram.get("available_mb", 8192.0), 2),
            "percent_used": sys_ram.get("used_pct", 50.0),
            "configured_budget_mb": settings.MAX_RAM_USAGE_MB,
        }

        return {
            "vram": vram_info,
            "ram": ram_info,
            "model_lifecycle": diag.get("model_lifecycle", {
                "max_concurrent_models": settings.MAX_CONCURRENT_MODELS,
                "strategy": "sequential_load_unload",
            }),
        }
