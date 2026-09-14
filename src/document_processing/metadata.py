"""
Metadata Extraction Module for MRPL AI Workbench.
Extracts and consolidates comprehensive metadata for processed documents and chunks.
"""

from datetime import datetime, timezone
from typing import List

from src.document_processing.chunker import DocumentChunk
from src.document_processing.loader import LoadedDocument
from src.document_processing.parser import ParsedDocument
from src.schemas.document import DocumentMetadataSchema


class MetadataExtractor:
    """
    Metadata Extractor aggregating file specs, cryptographic SHA-256 hashes,
    character/word statistics, chunk metrics, and UTC timestamps.
    """

    def extract_metadata(
        self,
        loaded_doc: LoadedDocument,
        parsed_doc: ParsedDocument,
        chunks: List[DocumentChunk],
        chunk_size: int,
        chunk_overlap: int,
    ) -> DocumentMetadataSchema:
        """
        Build DocumentMetadataSchema from pipeline stage artifacts.

        Args:
            loaded_doc: LoadedDocument container.
            parsed_doc: ParsedDocument container.
            chunks: List of DocumentChunk objects.
            chunk_size: Configured chunk character size.
            chunk_overlap: Configured chunk overlap.

        Returns:
            DocumentMetadataSchema instance.
        """
        now_utc = datetime.now(timezone.utc).isoformat()

        return DocumentMetadataSchema(
            file_name=loaded_doc.file_name,
            file_size_bytes=loaded_doc.file_size_bytes,
            file_extension=loaded_doc.file_extension,
            mime_type=loaded_doc.mime_type,
            file_hash=loaded_doc.file_hash,
            total_chunks=len(chunks),
            total_characters=parsed_doc.char_count,
            total_words=parsed_doc.word_count,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            processed_at=now_utc,
        )
