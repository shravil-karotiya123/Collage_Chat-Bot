"""
Automatic Model Routing Package.
Provides intelligent request classification and local model routing abstractions.
"""

from src.routing.base_router import BaseRouter, RoutingResult
from src.routing.intent_classifier import ClassificationResult, IntentClassifier, UserIntent
from src.routing.model_router import ModelRouter
from src.routing.router_factory import RouterFactory
from src.routing.routing_rules import RoutingRules

__all__ = [
    "BaseRouter",
    "RoutingResult",
    "UserIntent",
    "ClassificationResult",
    "IntentClassifier",
    "RoutingRules",
    "ModelRouter",
    "RouterFactory",
]
