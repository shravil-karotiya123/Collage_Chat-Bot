"""
Models API endpoint.
Lists available local models, default tags, and architecture capability specs.
"""

from typing import Annotated, Any, Dict, List
from fastapi import APIRouter, Depends

from config.settings import settings
from src.api.dependencies import get_model_router
from src.api.responses.standard_response import StandardResponse, success_response
from src.models.deepseek_manager import DeepSeekManager
from src.models.qwen_manager import QwenManager
from src.models.vision_manager import VisionManager
from src.routing.base_router import BaseRouter

router = APIRouter(tags=["Models"])


@router.get(
    "/models",
    response_model=StandardResponse[Dict[str, Any]],
    summary="List Local AI Models & Specifications",
    description="Retrieve available local open-weight LLMs, active configuration tags, and model capability metadata.",
)
async def get_models(
    model_router: Annotated[BaseRouter, Depends(get_model_router)],
) -> StandardResponse[Dict[str, Any]]:
    """
    GET /models endpoint returning model specs from QwenManager, DeepSeekManager, and VisionManager.
    """
    qwen = QwenManager()
    deepseek = DeepSeekManager()
    vision = VisionManager()

    models_data = {
        "active_runtime": settings.ACTIVE_RUNTIME,
        "default_model": settings.DEFAULT_MODEL,
        "available_models": [
            {
                "tag": qwen.model_name,
                "role": "General AI",
                "manager": qwen.__class__.__name__,
                "metadata": qwen.get_metadata(),
            },
            {
                "tag": deepseek.model_name,
                "role": "Coding & Debugging",
                "manager": deepseek.__class__.__name__,
                "metadata": deepseek.get_metadata(),
            },
            {
                "tag": vision.model_name,
                "role": "Vision & Multimodal",
                "manager": vision.__class__.__name__,
                "metadata": vision.get_metadata(),
            },
        ],
    }

    return success_response(
        data=models_data,
        message="Local model specifications retrieved successfully",
    )
