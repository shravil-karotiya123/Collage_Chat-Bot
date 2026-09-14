"""
PDF Page Classification & Content Detection Module for MRPL AI Workbench.
Determines whether PDF pages are machine-readable text, scanned images, or mixed content.
Prevents unnecessary OCR on pages with sufficient text.
"""

import io
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import pypdf

logger = logging.getLogger("MRPL.OCR.PDFDetector")


class PDFPageType(str, Enum):
    """
    Page content classification tags.
    """

    TEXT = "TEXT"
    SCANNED_IMAGE = "SCANNED_IMAGE"
    MIXED = "MIXED"


@dataclass
class PageDetectionResult:
    """
    Structured result of PDF page content analysis.
    """

    page_number: int
    page_type: PDFPageType
    text_character_count: int
    image_count: int
    requires_ocr: bool
    extracted_text: str


class PDFDetector:
    """
    PDF Content Detector analyzing page streams to classify machine-readable vs scanned pages.
    Optimizes hardware resource allocation by skipping OCR on clear text pages.
    """

    MIN_TEXT_CHAR_THRESHOLD: int = 50

    def detect_pdf_pages(self, pdf_bytes: bytes) -> List[PageDetectionResult]:
        """
        Analyze all pages of a PDF document payload.

        Args:
            pdf_bytes: PDF byte payload.

        Returns:
            List of PageDetectionResult objects.
        """
        results: List[PageDetectionResult] = []
        try:
            stream = io.BytesIO(pdf_bytes)
            reader = pypdf.PdfReader(stream)

            for idx, page in enumerate(reader.pages):
                page_num = idx + 1
                page_text = (page.extract_text() or "").strip()
                char_count = len(page_text)

                image_count = len(page.images) if hasattr(page, "images") else 0

                if char_count >= self.MIN_TEXT_CHAR_THRESHOLD and image_count == 0:
                    page_type = PDFPageType.TEXT
                    requires_ocr = False
                elif char_count < self.MIN_TEXT_CHAR_THRESHOLD and image_count > 0:
                    page_type = PDFPageType.SCANNED_IMAGE
                    requires_ocr = True
                elif char_count >= self.MIN_TEXT_CHAR_THRESHOLD and image_count > 0:
                    page_type = PDFPageType.MIXED
                    requires_ocr = False
                elif char_count > 0:
                    page_type = PDFPageType.TEXT
                    requires_ocr = False
                else:
                    page_type = PDFPageType.SCANNED_IMAGE
                    requires_ocr = True

                results.append(
                    PageDetectionResult(
                        page_number=page_num,
                        page_type=page_type,
                        text_character_count=char_count,
                        image_count=image_count,
                        requires_ocr=requires_ocr,
                        extracted_text=page_text,
                    )
                )

        except Exception as exc:
            logger.warning(f"PDF content detection failed ({str(exc)}), marking fallback scanned.")
            results.append(
                PageDetectionResult(
                    page_number=1,
                    page_type=PDFPageType.SCANNED_IMAGE,
                    text_character_count=0,
                    image_count=1,
                    requires_ocr=True,
                    extracted_text="",
                )
            )

        return results
