"""
Chat API endpoint.
Handles chat interaction requests delegating strictly to ChatService.
"""

from typing import Annotated
from fastapi import APIRouter, Depends

from src.api.dependencies import get_chat_service
from src.api.responses.standard_response import StandardResponse, success_response
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService

router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=StandardResponse[ChatResponse],
    summary="Process Chat Interaction Turn",
    description="Route user query prompt to appropriate local LLM manager via Intelligent Model Router.",
)
async def process_chat(
    request: ChatRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> StandardResponse[ChatResponse]:
    """
    POST /chat endpoint delegating request processing exclusively to ChatService.
    """
    # Delegate strictly to ChatService layer
    turn_result = await chat_service.process_chat_turn(
        query=request.query,
        context=request.context,
        temperature=request.temperature,
    )

    chat_response = ChatResponse(
        text=turn_result["text"],
        model_used=turn_result["model_used"],
        intent=turn_result.get("intent"),
        confidence=turn_result.get("confidence"),
        routing_time_ms=turn_result.get("routing_time_ms"),
        status=turn_result.get("status", "SUCCESS"),
        tokens_generated=turn_result.get("tokens_generated", 0),
        execution_time_seconds=turn_result.get("execution_time_seconds", 0.0),
        metadata=turn_result.get("metadata", {}),
    )

    return success_response(
        data=chat_response,
        message="Chat response generated successfully",
    )
