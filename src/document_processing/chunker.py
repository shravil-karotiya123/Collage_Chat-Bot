"""
Document Text Chunker Module for MRPL AI Workbench.
Splits parsed document text into structured chunks with configurable chunk size and overlap.
"""

from dataclasses import dataclass
from typing import List, Optional

from config.settings import settings


@dataclass
class DocumentChunk:
    """
    Standard text chunk unit prepared for downstream RAG vector indexing.
    """

    chunk_id: int
    content: str
    start_char: int
    end_char: int
    word_count: int


class DocumentChunker:
    """
    Production-grade text chunker splitting document text into overlapping character chunks.
    Supports smart splitting on paragraph, sentence, and word boundaries.
    """

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> None:
        self.chunk_size = settings.DEFAULT_CHUNK_SIZE if chunk_size is None else chunk_size
        self.chunk_overlap = settings.DEFAULT_CHUNK_OVERLAP if chunk_overlap is None else chunk_overlap

        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")
        if self.chunk_overlap < 0 or self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be non-negative and strictly less than chunk_size.")

    def chunk_text(self, text: str) -> List[DocumentChunk]:
        """
        Chunk string text into a list of DocumentChunk objects.

        Args:
            text: Raw input text.

        Returns:
            List of DocumentChunk instances.
        """
        cleaned_text = text.strip() if text else ""
        if not cleaned_text:
            return []

        text_length = len(cleaned_text)

        # Short text case: single chunk
        if text_length <= self.chunk_size:
            return [
                DocumentChunk(
                    chunk_id=0,
                    content=cleaned_text,
                    start_char=0,
                    end_char=text_length,
                    word_count=len(cleaned_text.split()),
                )
            ]

        chunks: List[DocumentChunk] = []
        start = 0
        chunk_id = 0
        step = self.chunk_size - self.chunk_overlap

        while start < text_length:
            end = start + self.chunk_size

            # If not at the end of the text, look for clean boundary breakpoint
            if end < text_length:
                best_break = -1
                search_buffer = cleaned_text[start:end]

                # Look for paragraph break (\n\n), newline (\n), sentence end (. ), or space
                for separator in ["\n\n", "\n", ". ", " "]:
                    pos = search_buffer.rfind(separator)
                    if pos != -1 and pos > int(self.chunk_size * 0.4):
                        best_break = start + pos + len(separator)
                        break

                if best_break != -1:
                    end = best_break

            chunk_content = cleaned_text[start:end].strip()
            if chunk_content:
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        content=chunk_content,
                        start_char=start,
                        end_char=end,
                        word_count=len(chunk_content.split()),
                    )
                )
                chunk_id += 1

            if end >= text_length:
                break

            # Calculate next start offset ensuring progress
            next_start = end - self.chunk_overlap
            if next_start <= start:
                next_start = start + step

            start = next_start

        return chunks
