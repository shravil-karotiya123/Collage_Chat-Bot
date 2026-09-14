"""
Document Validation Module for MRPL AI Workbench.
Validates uploaded file extensions, file sizes, payload integrity, and SHA-256 hashes.
"""

import hashlib
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Set

from config.settings import settings


@dataclass
class ValidationResult:
    """
    Structured outcome of document validation analysis.
    """

    is_valid: bool
    file_name: str
    file_extension: str
    file_size_bytes: int
    file_hash: str
    mime_type: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DocumentValidator:
    """
    Production-grade document validator enforcing security boundaries,
    supported formats, size limits, and cryptographic SHA-256 hash computation.
    """

    SUPPORTED_EXTENSIONS: Set[str] = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
        ".csv",
        ".xlsx",
    }

    MIME_TYPES: Dict[str, str] = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    def __init__(self, max_size_bytes: Optional[int] = None) -> None:
        self.max_size_bytes = max_size_bytes or settings.MAX_DOCUMENT_SIZE_BYTES

    def validate(self, file_name: str, content: bytes) -> ValidationResult:
        """
        Validate uploaded document payload.

        Args:
            file_name: Name of uploaded file.
            content: Raw file content bytes.

        Returns:
            ValidationResult with validation flag, SHA-256 hash, and metadata.
        """
        ext = Path(file_name).suffix.lower()
        file_size = len(content)

        # Calculate SHA-256 Hash Digest
        file_hash = hashlib.sha256(content).hexdigest()

        # Resolve MIME Type
        mime_type = self.MIME_TYPES.get(ext) or mimetypes.guess_type(file_name)[0] or "application/octet-stream"

        # 1. Extension Validation
        if ext not in self.SUPPORTED_EXTENSIONS:
            return ValidationResult(
                is_valid=False,
                file_name=file_name,
                file_extension=ext,
                file_size_bytes=file_size,
                file_hash=file_hash,
                mime_type=mime_type,
                error_message=f"Unsupported file format '{ext}'. Supported formats: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}",
            )

        # 2. Empty Payload Validation
        if file_size == 0:
            return ValidationResult(
                is_valid=False,
                file_name=file_name,
                file_extension=ext,
                file_size_bytes=0,
                file_hash=file_hash,
                mime_type=mime_type,
                error_message="Uploaded file is empty (0 bytes).",
            )

        # 3. Maximum Size Validation
        if file_size > self.max_size_bytes:
            max_mb = self.max_size_bytes / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            return ValidationResult(
                is_valid=False,
                file_name=file_name,
                file_extension=ext,
                file_size_bytes=file_size,
                file_hash=file_hash,
                mime_type=mime_type,
                error_message=f"File size ({actual_mb:.2f} MB) exceeds maximum limit ({max_mb:.1f} MB).",
            )

        return ValidationResult(
            is_valid=True,
            file_name=file_name,
            file_extension=ext,
            file_size_bytes=file_size,
            file_hash=file_hash,
            mime_type=mime_type,
            error_message=None,
        )
