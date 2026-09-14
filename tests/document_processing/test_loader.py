"""
Unit tests for DocumentLoader module.
"""

from pathlib import Path
import pytest

from src.document_processing.loader import DocumentLoader, LoadedDocument


@pytest.fixture
def loader() -> DocumentLoader:
    return DocumentLoader()


def test_load_from_bytes(loader: DocumentLoader) -> None:
    content = b"MRPL AI Workbench refinery telemetry notes."
    loaded = loader.load_from_bytes("notes.txt", content)
    assert isinstance(loaded, LoadedDocument)
    assert loaded.file_name == "notes.txt"
    assert loaded.content_bytes == content
    assert loaded.file_extension == ".txt"
    assert loaded.file_size_bytes == len(content)
    assert len(loaded.file_hash) == 64


def test_load_from_bytes_invalid(loader: DocumentLoader) -> None:
    with pytest.raises(ValueError, match="validation failed"):
        loader.load_from_bytes("test.bin", b"invalid extension")


def test_load_from_path(loader: DocumentLoader, tmp_path: Path) -> None:
    file_path = tmp_path / "sample.md"
    file_path.write_text("# MRPL Architecture\nSample markdown document.")
    loaded = loader.load_from_path(file_path)
    assert loaded.file_name == "sample.md"
    assert loaded.file_extension == ".md"
    assert loaded.file_path == file_path.resolve()


def test_load_from_nonexistent_path(loader: DocumentLoader) -> None:
    with pytest.raises(FileNotFoundError):
        loader.load_from_path("non_existent_file.pdf")
