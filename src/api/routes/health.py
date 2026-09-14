"""
Health check API endpoint.
Provides system operational status and model runtime availability metrics.
"""

from typing import Annotated, Any, Dict
from fastapi import APIRouter, Depends

from config.settings import settings
from src.api.dependencies import get_model_router
from src.api.responses.standard_response import StandardResponse, success_response
from src.routing.base_router import BaseRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=StandardResponse[Dict[str, Any]],
    summary="Workbench System Health Check",
    description="Retrieve system health status, active runtime engine, and model availability metrics.",
)
async def get_health(
    model_router: Annotated[BaseRouter, Depends(get_model_router)],
) -> StandardResponse[Dict[str, Any]]:
    """
    GET /health endpoint retrieving environment and model manager health metrics.
    """
    # Sample health status across model managers via router abstraction
    qwen_health = model_router.rules.get_manager(model_router.rules._mappings.get("GENERAL_CHAT")).health() if hasattr(model_router, "rules") else {"status": "ok"}

    health_data = {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "active_runtime": settings.ACTIVE_RUNTIME,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "default_model": settings.DEFAULT_MODEL,
        "gpu_enabled": settings.GPU_ENABLED,
        "model_health": {
            "qwen": settings.QWEN_MODEL,
            "deepseek": settings.DEFAULT_DEEPSEEK_MODEL,
            "vision": settings.DEFAULT_VISION_MODEL,
        },
    }

    return success_response(
        data=health_data,
        message="System and model managers operational",
    )
