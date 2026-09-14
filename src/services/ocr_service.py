"""
OCR & Vision analysis service interface definition.
"""

from typing import Any, Dict


class OCRService:
    """
    Service layer contract for multimodal vision analysis of engineering diagrams and scanned document pages.
    """

    async def analyze_document_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Contract for analyzing structural diagrams, schematics, or scanned receipts.
        """
        raise NotImplementedError("Service interface contract only.")

    async def extract_structured_text(self, image_path: str) -> str:
        """
        Contract for extracting text from raw images via local multimodal LLMs.
        """
        raise NotImplementedError("Service interface contract only.")
