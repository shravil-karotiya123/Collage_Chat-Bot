"""
Document Processing Pipeline Module for MRPL AI Workbench.
Orchestrates end-to-end flow: Upload -> Validation -> Loader -> Parser -> Chunker -> Metadata -> Response.
"""

import logging
import time
from typing import Optional

from src.document_processing.chunker import DocumentChunker
from src.document_processing.loader import DocumentLoader
from src.document_processing.metadata import MetadataExtractor
from src.document_processing.parser import DocumentParser
from src.schemas.document import DocumentChunkSchema, DocumentUploadResponse

logger = logging.getLogger("MRPL.DocumentPipeline")


class DocumentProcessingPipeline:
    """
    Production-ready Document Processing Pipeline managing sequential execution stages
    and providing structured telemetry logging.
    """

    def __init__(
        self,
        loader: Optional[DocumentLoader] = None,
        parser: Optional[DocumentParser] = None,
        chunker: Optional[DocumentChunker] = None,
        metadata_extractor: Optional[MetadataExtractor] = None,
    ) -> None:
        self.loader = loader or DocumentLoader()
        self.parser = parser or DocumentParser()
        self.chunker = chunker or DocumentChunker()
        self.metadata_extractor = metadata_extractor or MetadataExtractor()

    def process_document(
        self,
        file_name: str,
        content: bytes,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> DocumentUploadResponse:
        """
        Execute document processing pipeline stages sequentially.

        Args:
            file_name: Original file name.
            content: Raw document byte payload.
            chunk_size: Optional custom chunk character limit.
            chunk_overlap: Optional custom chunk character overlap.

        Returns:
            DocumentUploadResponse object containing metadata and chunk list.
        """
        start_time = time.perf_counter()

        # 1. Load & Validate Document
        loaded_doc = self.loader.load_from_bytes(file_name=file_name, content=content)

        # 2. Parse Text & Structural Metadata
        parsed_doc = self.parser.parse(loaded_doc)

        # 3. Chunk Text
        active_chunker = (
            DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            if (chunk_size or chunk_overlap)
            else self.chunker
        )
        chunks = active_chunker.chunk_text(parsed_doc.text_content)

        # 4. Extract Metadata Specifications
        metadata_schema = self.metadata_extractor.extract_metadata(
            loaded_doc=loaded_doc,
            parsed_doc=parsed_doc,
            chunks=chunks,
            chunk_size=active_chunker.chunk_size,
            chunk_overlap=active_chunker.chunk_overlap,
        )

        # 5. Format Output Chunks Schema
        chunk_schemas = [
            DocumentChunkSchema(
                chunk_id=c.chunk_id,
                content=c.content,
                start_char=c.start_char,
                end_char=c.end_char,
                word_count=c.word_count,
            )
            for c in chunks
        ]

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        logger.info(
            f"[DOCUMENT PIPELINE] processed_file='{file_name}' | "
            f"hash={loaded_doc.file_hash[:12]} | "
            f"size_bytes={loaded_doc.file_size_bytes} | "
            f"total_chunks={len(chunks)} | "
            f"duration={duration_ms:.2f}ms"
        )

        return DocumentUploadResponse(
            metadata=metadata_schema,
            chunks=chunk_schemas,
            status="SUCCESS",
        )
