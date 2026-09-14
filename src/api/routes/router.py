"""
Router metadata API endpoint.
Provides current router configuration, intent mappings, and classification settings.
"""

from typing import Annotated, Any, Dict
from fastapi import APIRouter, Depends

from config.settings import settings
from src.api.dependencies import get_model_router
from src.api.responses.standard_response import StandardResponse, success_response
from src.routing.base_router import BaseRouter
from src.routing.model_router import ModelRouter

router = APIRouter(tags=["Router"])


@router.get(
    "/router",
    response_model=StandardResponse[Dict[str, Any]],
    summary="Get Intelligent Router Configuration",
    description="Retrieve router class name, intent-to-manager mapping table, and configuration settings.",
)
async def get_router_info(
    model_router: Annotated[BaseRouter, Depends(get_model_router)],
) -> StandardResponse[Dict[str, Any]]:
    """
    GET /router endpoint inspecting active router configurations and rules.
    """
    router_class_name = model_router.__class__.__name__

    intent_mappings = {}
    if isinstance(model_router, ModelRouter):
        intent_mappings = model_router.rules.get_all_mappings()

    router_data = {
        "router_class": router_class_name,
        "router_type": settings.ROUTER_TYPE,
        "enable_confidence": settings.ENABLE_CONFIDENCE,
        "enable_routing_logs": settings.ENABLE_ROUTING_LOGS,
        "default_model": settings.DEFAULT_MODEL,
        "intent_mappings": intent_mappings,
        "supported_intents": [
            "GENERAL_CHAT",
            "DOCUMENT",
            "APPROVAL_NOTE",
            "SUMMARIZATION",
            "CODING",
            "DEBUGGING",
            "IMAGE",
            "OCR",
            "DIAGRAM",
            "UNKNOWN",
        ],
    }

    return success_response(
        data=router_data,
        message="Intelligent Router configuration retrieved successfully",
    )
