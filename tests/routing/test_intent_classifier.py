"""
Unit tests for IntentClassifier engine.
Verifies accuracy across all 10 intent categories, context parameters, and fallback logic.
"""

import pytest
from src.routing.intent_classifier import IntentClassifier, UserIntent


@pytest.fixture
def classifier() -> IntentClassifier:
    return IntentClassifier()


def test_classify_general_chat(classifier: IntentClassifier) -> None:
    res = classifier.classify("Hello, good morning! How can you assist me today?")
    assert res.intent == UserIntent.GENERAL_CHAT
    assert res.confidence > 0.5


def test_classify_document(classifier: IntentClassifier) -> None:
    res = classifier.classify("Draft a formal report document template for management.")
    assert res.intent == UserIntent.DOCUMENT
    assert res.confidence > 0.7


def test_classify_approval_note(classifier: IntentClassifier) -> None:
    res = classifier.classify("Prepare an approval note for financial sanction of refinery equipment.")
    assert res.intent == UserIntent.APPROVAL_NOTE
    assert res.confidence > 0.8


def test_classify_summarization(classifier: IntentClassifier) -> None:
    res = classifier.classify("Please summarize key takeaways and give me a tl;dr overview.")
    assert res.intent == UserIntent.SUMMARIZATION
    assert res.confidence > 0.8


def test_classify_coding(classifier: IntentClassifier) -> None:
    res = classifier.classify("Write a python function to parse json data from api endpoint.")
    assert res.intent == UserIntent.CODING
    assert res.confidence > 0.8


def test_classify_debugging(classifier: IntentClassifier) -> None:
    res = classifier.classify("Fix bug causing SyntaxError and NullPointer exception in stack trace.")
    assert res.intent == UserIntent.DEBUGGING
    assert res.confidence > 0.8


def test_classify_image(classifier: IntentClassifier) -> None:
    res = classifier.classify("Describe this picture from visual inspection of the site.")
    assert res.intent == UserIntent.IMAGE
    assert res.confidence > 0.7


def test_classify_ocr(classifier: IntentClassifier) -> None:
    res = classifier.classify("Perform OCR to extract text from scanned image file.")
    assert res.intent == UserIntent.OCR
    assert res.confidence > 0.8


def test_classify_diagram(classifier: IntentClassifier) -> None:
    res = classifier.classify("Analyze process flow diagram and P&ID schematic for refinery unit.")
    assert res.intent == UserIntent.DIAGRAM
    assert res.confidence > 0.8


def test_classify_unknown_empty(classifier: IntentClassifier) -> None:
    res = classifier.classify("")
    assert res.intent == UserIntent.UNKNOWN
    assert res.confidence == 0.0


def test_context_image_override(classifier: IntentClassifier) -> None:
    context = {"file_path": "c:/data/inspection.png", "has_image": True}
    res = classifier.classify("What do you see here?", context=context)
    assert res.intent == UserIntent.IMAGE
    assert res.confidence >= 0.95


def test_context_image_ocr_override(classifier: IntentClassifier) -> None:
    context = {"file_path": "c:/data/scan.jpg"}
    res = classifier.classify("Extract text from this image", context=context)
    assert res.intent == UserIntent.OCR
    assert res.confidence >= 0.95


def test_heuristic_code_syntax(classifier: IntentClassifier) -> None:
    res = classifier.classify("```\ndef test_fn():\n    return True\n```")
    assert res.intent == UserIntent.CODING
    assert res.confidence >= 0.85
