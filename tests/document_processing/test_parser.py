"""
Unit tests for DocumentParser formats parsing strategies.
"""

import io
import docx
import pypdf
import pytest

from src.document_processing.loader import LoadedDocument
from src.document_processing.parser import DocumentParser, ParsedDocument


@pytest.fixture
def parser() -> DocumentParser:
    return DocumentParser()


def test_parse_text_document(parser: DocumentParser) -> None:
    doc = LoadedDocument(
        file_name="guide.txt",
        content_bytes=b"Line 1: Refinery operations.\nLine 2: Safety protocol.",
        file_extension=".txt",
        file_size_bytes=52,
        file_hash="hash123",
        mime_type="text/plain",
    )
    parsed = parser.parse(doc)
    assert isinstance(parsed, ParsedDocument)
    assert "Refinery operations" in parsed.text_content
    assert parsed.word_count == 8
    assert parsed.char_count > 0


def test_parse_markdown_document(parser: DocumentParser) -> None:
    doc = LoadedDocument(
        file_name="README.md",
        content_bytes=b"# Title\n\n## Section 1\nSome text content.",
        file_extension=".md",
        file_size_bytes=42,
        file_hash="hash123",
        mime_type="text/markdown",
    )
    parsed = parser.parse(doc)
    assert "# Title" in parsed.text_content
    assert "Section 1" in parsed.text_content


def test_parse_csv_document(parser: DocumentParser) -> None:
    csv_bytes = b"Name,Age,Role\nAlice,30,Engineer\nBob,35,Manager"
    doc = LoadedDocument(
        file_name="data.csv",
        content_bytes=csv_bytes,
        file_extension=".csv",
        file_size_bytes=len(csv_bytes),
        file_hash="hash123",
        mime_type="text/csv",
    )
    parsed = parser.parse(doc)
    assert "Headers: Name | Age | Role" in parsed.text_content
    assert "Row 1: Alice | 30 | Engineer" in parsed.text_content
    assert parsed.metadata["row_count"] == 3


def test_parse_docx_document(parser: DocumentParser) -> None:
    # Create in-memory docx file
    doc_obj = docx.Document()
    doc_obj.add_paragraph("Refinery Sanction Note 2026.")
    table = doc_obj.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Item"
    table.rows[0].cells[1].text = "Cost"

    buffer = io.BytesIO()
    doc_obj.save(buffer)
    docx_bytes = buffer.getvalue()

    doc = LoadedDocument(
        file_name="sanction.docx",
        content_bytes=docx_bytes,
        file_extension=".docx",
        file_size_bytes=len(docx_bytes),
        file_hash="hash123",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    parsed = parser.parse(doc)
    assert "Refinery Sanction Note 2026" in parsed.text_content
    assert "Item | Cost" in parsed.text_content


def test_parse_pdf_document(parser: DocumentParser) -> None:
    # Create in-memory PDF using pypdf writer
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    buffer = io.BytesIO()
    writer.write(buffer)
    pdf_bytes = buffer.getvalue()

    doc = LoadedDocument(
        file_name="report.pdf",
        content_bytes=pdf_bytes,
        file_extension=".pdf",
        file_size_bytes=len(pdf_bytes),
        file_hash="hash123",
        mime_type="application/pdf",
    )

    parsed = parser.parse(doc)
    assert isinstance(parsed, ParsedDocument)
    assert parsed.page_or_sheet_count == 1
