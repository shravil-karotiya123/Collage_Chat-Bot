"""
Unit tests for RouterFactory construction logic.
"""

from src.routing.base_router import BaseRouter
from src.routing.intent_classifier import IntentClassifier
from src.routing.model_router import ModelRouter
from src.routing.router_factory import RouterFactory
from src.routing.routing_rules import RoutingRules


def test_create_default_router() -> None:
    router = RouterFactory.create_router()
    assert isinstance(router, BaseRouter)
    assert isinstance(router, ModelRouter)


def test_create_intent_router() -> None:
    router = RouterFactory.create_router(router_type="intent")
    assert isinstance(router, ModelRouter)


def test_create_router_with_custom_deps() -> None:
    custom_classifier = IntentClassifier()
    custom_rules = RoutingRules()
    router = RouterFactory.create_router(
        router_type="intelligent",
        classifier=custom_classifier,
        rules=custom_rules,
    )
    assert isinstance(router, ModelRouter)
    assert router.classifier is custom_classifier
    assert router.rules is custom_rules
