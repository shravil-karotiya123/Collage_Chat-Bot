"""
Unit tests for MetadataExtractor module.
"""

from src.document_processing.chunker import DocumentChunk
from src.document_processing.loader import LoadedDocument
from src.document_processing.metadata import MetadataExtractor
from src.document_processing.parser import ParsedDocument


def test_extract_metadata() -> None:
    extractor = MetadataExtractor()
    loaded_doc = LoadedDocument(
        file_name="spec.pdf",
        content_bytes=b"pdf content bytes",
        file_extension=".pdf",
        file_size_bytes=17,
        file_hash="hash_abc_123",
        mime_type="application/pdf",
    )
    parsed_doc = ParsedDocument(
        text_content="Parsed text content for specification document.",
        char_count=47,
        word_count=6,
        page_or_sheet_count=1,
    )
    chunks = [
        DocumentChunk(
            chunk_id=0,
            content="Parsed text content for specification document.",
            start_char=0,
            end_char=47,
            word_count=6,
        )
    ]

    meta = extractor.extract_metadata(
        loaded_doc=loaded_doc,
        parsed_doc=parsed_doc,
        chunks=chunks,
        chunk_size=1000,
        chunk_overlap=200,
    )

    assert meta.file_name == "spec.pdf"
    assert meta.file_size_bytes == 17
    assert meta.file_extension == ".pdf"
    assert meta.file_hash == "hash_abc_123"
    assert meta.total_chunks == 1
    assert meta.total_characters == 47
    assert meta.total_words == 6
    assert meta.chunk_size == 1000
    assert meta.chunk_overlap == 200
    assert "T" in meta.processed_at  # ISO 8601 UTC string
