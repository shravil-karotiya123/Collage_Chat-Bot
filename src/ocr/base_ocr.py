"""
Abstract Base OCR Interface Module for MRPL AI Workbench.
Defines replaceable contracts for OCR and vision extraction engines.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseOCR(ABC):
    """
    Abstract Base Class contract for OCR extraction engines.
    Ensures OCR implementations remain pluggable and decoupled.
    """

    @abstractmethod
    def process_image(
        self,
        image_bytes: bytes,
        filename: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Extract text and metadata from raw image bytes.

        Args:
            image_bytes: Raw image payload bytes.
            filename: Name of file.

        Returns:
            Dict containing 'text', 'confidence', 'method', and 'metadata'.
        """
        pass

    @abstractmethod
    def process_page(
        self,
        page_bytes: bytes,
        page_number: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Extract text from an individual document page.

        Args:
            page_bytes: Raw page payload or image bytes.
            page_number: 1-based page index.

        Returns:
            Dict containing page extraction details.
        """
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Query OCR engine operational status."""
        pass
