"""
Vision Analyzer Module for MRPL AI Workbench.
Delegates visual analysis of technical diagrams, schematics, and scanned pages to VisionManager (minicpm-v:8b).
Never calls Ollama directly.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from src.ocr.image_processor import ImageProcessor, ProcessedImage

if TYPE_CHECKING:
    from src.models.base_model import BaseModel

logger = logging.getLogger("MRPL.OCR.VisionAnalyzer")

DEFAULT_OCR_TEXT_PROMPT = "Transcribe all text from this scanned document page accurately without omission."
DEFAULT_DIAGRAM_PROMPT = "Analyze this engineering diagram or schematic. List key components, equipment IDs, labels, and flow directions."


class VisionAnalyzer:
    """
    Vision Analyzer performing multimodal visual understanding using VisionManager.
    Protects memory by ensuring temporary disk images are created and purged safely.
    """

    def __init__(
        self,
        vision_manager: Optional[Any] = None,
        image_processor: Optional[ImageProcessor] = None,
    ) -> None:
        from src.models.vision_manager import VisionManager
        self.vision_manager = vision_manager or VisionManager()
        self.image_processor = image_processor or ImageProcessor()

    def extract_text_from_image(
        self,
        processed_image: ProcessedImage,
        prompt: Optional[str] = None,
    ) -> str:
        """
        Extract text from a processed image using VisionManager.

        Args:
            processed_image: ProcessedImage container.
            prompt: Optional prompt override.

        Returns:
            Extracted text string.
        """
        target_prompt = prompt or DEFAULT_OCR_TEXT_PROMPT
        temp_path = self.image_processor.create_temp_image_file(processed_image)

        try:
            if hasattr(self.vision_manager, "analyze_image"):
                extracted = self.vision_manager.analyze_image(
                    image_path=str(temp_path),
                    prompt=target_prompt,
                )
            else:
                extracted = self.vision_manager.generate(
                    prompt=f"[IMAGE: {temp_path}] {target_prompt}",
                )
            return (extracted or "").strip()

        finally:
            self.image_processor.cleanup_temp_file(temp_path)

    def analyze_diagram(
        self,
        processed_image: ProcessedImage,
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform detailed visual inspection and component analysis of engineering diagrams.

        Args:
            processed_image: ProcessedImage container.
            prompt: Optional custom analysis prompt.

        Returns:
            Dict containing visual analysis breakdown and metadata.
        """
        target_prompt = prompt or DEFAULT_DIAGRAM_PROMPT
        analysis_text = self.extract_text_from_image(processed_image, prompt=target_prompt)

        return {
            "filename": processed_image.filename,
            "width": processed_image.width,
            "height": processed_image.height,
            "visual_analysis": analysis_text,
            "model_used": self.vision_manager.model_name,
            "capabilities_used": ["diagram_analysis", "visual_inspection"],
        }
