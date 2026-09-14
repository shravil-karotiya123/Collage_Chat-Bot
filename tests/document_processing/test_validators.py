"""
Unit tests for DocumentValidator module.
"""

import pytest
from src.document_processing.validators import DocumentValidator


@pytest.fixture
def validator() -> DocumentValidator:
    return DocumentValidator(max_size_bytes=1024 * 1024)  # 1 MB limit for testing


def test_valid_text_document(validator: DocumentValidator) -> None:
    res = validator.validate("report.txt", b"Sample text content for testing.")
    assert res.is_valid is True
    assert res.file_extension == ".txt"
    assert res.file_size_bytes > 0
    assert len(res.file_hash) == 64  # SHA-256 hex length
    assert res.mime_type == "text/plain"
    assert res.error_message is None


def test_valid_supported_extensions(validator: DocumentValidator) -> None:
    extensions = ["sample.pdf", "doc.docx", "readme.md", "data.csv", "sheet.xlsx"]
    for fname in extensions:
        res = validator.validate(fname, b"dummy data payload")
        assert res.is_valid is True
        assert res.error_message is None


def test_unsupported_format(validator: DocumentValidator) -> None:
    res = validator.validate("script.exe", b"binary content")
    assert res.is_valid is False
    assert "Unsupported file format" in res.error_message


def test_empty_file_validation(validator: DocumentValidator) -> None:
    res = validator.validate("empty.txt", b"")
    assert res.is_valid is False
    assert "empty" in res.error_message.lower()


def test_max_size_exceeded(validator: DocumentValidator) -> None:
    large_payload = b"X" * (1024 * 1024 + 10)  # > 1 MB
    res = validator.validate("large.txt", large_payload)
    assert res.is_valid is False
    assert "exceeds maximum limit" in res.error_message
