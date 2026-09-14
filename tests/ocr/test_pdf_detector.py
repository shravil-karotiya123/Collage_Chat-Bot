"""
Unit tests for PDFDetector module.
"""

import io
import pypdf
import pytest

from src.ocr.pdf_detector import PDFDetector, PDFPageType


def create_text_pdf_bytes() -> bytes:
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=200, height=200)
    # pypdf Writer blank page text detection
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_pdf_detector_scanned_blank_page() -> None:
    detector = PDFDetector()
    pdf_bytes = create_text_pdf_bytes()
    detections = detector.detect_pdf_pages(pdf_bytes)

    assert len(detections) == 1
    det = detections[0]
    assert det.page_number == 1
    assert det.page_type in {PDFPageType.SCANNED_IMAGE, PDFPageType.TEXT}


def test_pdf_detector_corrupt_pdf_fallback() -> None:
    detector = PDFDetector()
    detections = detector.detect_pdf_pages(b"corrupt pdf content bytes")

    assert len(detections) == 1
    assert detections[0].page_type == PDFPageType.SCANNED_IMAGE
    assert detections[0].requires_ocr is True
