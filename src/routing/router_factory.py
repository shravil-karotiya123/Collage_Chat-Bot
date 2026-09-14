"""
Router Factory Module for MRPL AI Workbench.
Constructs router instances adhering to SOLID factory design pattern.
"""

from typing import Optional

from config.settings import settings
from src.routing.base_router import BaseRouter
from src.routing.intent_classifier import IntentClassifier
from src.routing.model_router import ModelRouter
from src.routing.routing_rules import RoutingRules


class RouterFactory:
    """
    Factory class responsible for instantiating model router variants based on settings or explicit specification.
    """

    @staticmethod
    def create_router(
        router_type: Optional[str] = None,
        classifier: Optional[IntentClassifier] = None,
        rules: Optional[RoutingRules] = None,
    ) -> BaseRouter:
        """
        Create and return a router instance implementing BaseRouter interface.

        Args:
            router_type: Optional string indicator ("intent", "rule_based", "default").
            classifier: Optional custom IntentClassifier instance.
            rules: Optional custom RoutingRules instance.

        Returns:
            BaseRouter concrete instance (e.g., ModelRouter).
        """
        target_type = (router_type or settings.ROUTER_TYPE or "intent").lower()

        if target_type in {"intent", "rule_based", "default", "intelligent"}:
            return ModelRouter(classifier=classifier, rules=rules)
        else:
            # Fallback to standard ModelRouter
            return ModelRouter(classifier=classifier, rules=rules)
