"""
Document Loader Module for MRPL AI Workbench.
Handles reading raw document bytes and stream payloads into standard LoadedDocument containers.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from src.document_processing.validators import DocumentValidator, ValidationResult


@dataclass
class LoadedDocument:
    """
    Standard container encapsulating raw document payload and validation metadata.
    """

    file_name: str
    content_bytes: bytes
    file_extension: str
    file_size_bytes: int
    file_hash: str
    mime_type: str
    file_path: Optional[Path] = None


class DocumentLoader:
    """
    Document Loader responsible for reading raw document streams and local filesystem assets.
    Delegates validation to DocumentValidator.
    """

    def __init__(self, validator: Optional[DocumentValidator] = None) -> None:
        self.validator = validator or DocumentValidator()

    def load_from_bytes(self, file_name: str, content: bytes) -> LoadedDocument:
        """
        Load document from byte string payload.

        Args:
            file_name: Name of file.
            content: Raw byte payload.

        Returns:
            LoadedDocument container object.

        Raises:
            ValueError: If document fails validation rules.
        """
        val_result: ValidationResult = self.validator.validate(file_name, content)
        if not val_result.is_valid:
            raise ValueError(f"Document validation failed: {val_result.error_message}")

        return LoadedDocument(
            file_name=val_result.file_name,
            content_bytes=content,
            file_extension=val_result.file_extension,
            file_size_bytes=val_result.file_size_bytes,
            file_hash=val_result.file_hash,
            mime_type=val_result.mime_type,
            file_path=None,
        )

    def load_from_path(self, file_path: Union[str, Path]) -> LoadedDocument:
        """
        Load document from local file path.

        Args:
            file_path: Absolute or relative Path or string.

        Returns:
            LoadedDocument container object.
        """
        path = Path(file_path).resolve()
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Target document file does not exist: {path}")

        content = path.read_bytes()
        loaded_doc = self.load_from_bytes(file_name=path.name, content=content)
        loaded_doc.file_path = path
        return loaded_doc
