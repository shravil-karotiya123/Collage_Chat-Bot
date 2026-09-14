"""
Abstract base router interface specification and routing result DTO.
Defines contracts for routing user requests to local model managers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from src.models.base_model import BaseModel


@dataclass
class RoutingResult:
    """
    Structured response payload returned by model routing operations.
    Encapsulates selected model manager, classification metadata, and routing telemetry.
    """

    manager: Any
    selected_model: str
    intent: str
    confidence: float
    routing_time_ms: float
    status: str
    user_query: str
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert routing result to serializable dictionary for logging/telemetry."""
        return {
            "user_query": self.user_query,
            "detected_intent": self.intent,
            "selected_model": self.selected_model,
            "manager_class": self.manager.__class__.__name__,
            "confidence": round(self.confidence, 4),
            "routing_time_ms": round(self.routing_time_ms, 3),
            "status": self.status,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
        }


class BaseRouter(ABC):
    """
    Abstract Base Class defining the contract for all intelligent model router implementations.
    Decoupled entirely from specific runtime engines and direct network APIs.
    """

    @abstractmethod
    def route(
        self,
        request: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> RoutingResult:
        """
        Route incoming user request to appropriate local model manager.

        Args:
            request: Raw user input text/query.
            context: Optional contextual parameters (e.g. file paths, image indicators).

        Returns:
            RoutingResult encapsulation containing selected model manager and telemetry.
        """
        pass

    def get_manager(
        self,
        request: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> BaseModel:
        """
        Convenience accessor returning exclusively the target BaseModel manager instance.

        Args:
            request: Raw user input text/query.
            context: Optional contextual parameters.

        Returns:
            Target BaseModel manager implementation (QwenManager, DeepSeekManager, or VisionManager).
        """
        result = self.route(request=request, context=context)
        return result.manager
