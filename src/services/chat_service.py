"""
Chat service implementation for MRPL AI Workbench.
Coordinates conversational AI turns using Intelligent Model Router.
"""

import time
from typing import Any, AsyncGenerator, Dict, Optional

from src.models.vision_manager import VisionManager
from src.routing.base_router import BaseRouter
from src.routing.router_factory import RouterFactory


class ChatService:
    """
    Service layer orchestrating conversational chat turns and local LLM execution.
    Delegates all model selection to BaseRouter.
    """

    def __init__(self, router: Optional[BaseRouter] = None) -> None:
        self.router = router or RouterFactory.create_router()

    async def process_chat_turn(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Process a single chat interaction turn using routed local LLMs.

        Args:
            query: Raw user prompt string.
            context: Optional context dictionary (file paths, image flags, etc.).
            kwargs: Hyperparameters passed to model generation.

        Returns:
            Structured response dictionary containing generated text and routing telemetry.
        """
        ctx = context or {}
        start_time = time.perf_counter()

        # 1. Route query to optimal local model manager
        routing_result = self.router.route(request=query, context=ctx)
        manager = routing_result.manager

        # 2. Execute inference on selected model manager
        image_path = ctx.get("image_path") or ctx.get("file_path")
        if image_path and isinstance(manager, VisionManager):
            generated_text = manager.analyze_image(
                image_path=image_path,
                prompt=query,
                **kwargs,
            )
        else:
            generated_text = manager.generate(prompt=query, **kwargs)

        exec_time_seconds = time.perf_counter() - start_time
        estimated_tokens = len(generated_text.split()) if generated_text else 0

        return {
            "text": generated_text,
            "model_used": routing_result.selected_model,
            "intent": routing_result.intent,
            "confidence": routing_result.confidence,
            "routing_time_ms": routing_result.routing_time_ms,
            "status": routing_result.status,
            "tokens_generated": estimated_tokens,
            "execution_time_seconds": round(exec_time_seconds, 4),
            "metadata": routing_result.metadata,
        }

    async def stream_chat_turn(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat tokens for interactive UI consumption.
        """
        ctx = context or {}
        routing_result = self.router.route(request=query, context=ctx)
        manager = routing_result.manager

        async for chunk in manager.stream(prompt=query, **kwargs):
            yield chunk
