"""
OCR and Vision Intelligence Package for MRPL AI Workbench.
Provides PDF content detection, image preprocessing, OCR extraction,
multimodal vision analysis, and Phase 5/Phase 6 RAG pipeline integration.
"""

from src.ocr.base_ocr import BaseOCR
from src.ocr.image_processor import ImageProcessor, ProcessedImage
from src.ocr.ocr_pipeline import OCRPipeline
from src.ocr.ocr_service import OCRService
from src.ocr.pdf_detector import PageDetectionResult, PDFDetector, PDFPageType
from src.ocr.text_ocr import TextOCREngine
from src.ocr.vision_analyzer import VisionAnalyzer

__all__ = [
    "BaseOCR",
    "PDFPageType",
    "PageDetectionResult",
    "PDFDetector",
    "ProcessedImage",
    "ImageProcessor",
    "TextOCREngine",
    "VisionAnalyzer",
    "OCRPipeline",
    "OCRService",
]
