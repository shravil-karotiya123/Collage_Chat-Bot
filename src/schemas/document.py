"""
Document processing request and response schema models.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentProcessRequest(BaseModel):
    """Document processing/generation request schema."""

    document_type: str = Field(..., description="Target document type: docx or xlsx")
    title: str = Field(..., description="Document title")
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured content payload")
    template_name: Optional[str] = Field(default=None, description="Optional document template identifier")


class DocumentProcessResponse(BaseModel):
    """Document processing outcome schema."""

    output_path: str = Field(..., description="File path to generated export artifact")
    file_size_bytes: int = Field(default=0, description="Size of generated file in bytes")
    status: str = Field(default="completed", description="Generation execution status")


class DocumentChunkSchema(BaseModel):
    """Structured text chunk model for RAG preparation."""

    chunk_id: int = Field(..., description="Zero-based sequence index of chunk")
    content: str = Field(..., description="Cleaned chunk text content")
    start_char: int = Field(..., description="Starting character offset in source text")
    end_char: int = Field(..., description="Ending character offset in source text")
    word_count: int = Field(..., description="Word count in chunk text")


class DocumentMetadataSchema(BaseModel):
    """Extracted metadata specs for uploaded document."""

    file_name: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(..., description="File size in bytes")
    file_extension: str = Field(..., description="Normalized file extension (e.g. .pdf)")
    mime_type: str = Field(..., description="Detected MIME type")
    file_hash: str = Field(..., description="SHA-256 hash digest")
    total_chunks: int = Field(..., description="Total chunks generated")
    total_characters: int = Field(..., description="Total characters extracted")
    total_words: int = Field(..., description="Total word count")
    chunk_size: int = Field(..., description="Configured chunk character limit")
    chunk_overlap: int = Field(..., description="Configured chunk overlap")
    processed_at: str = Field(..., description="ISO 8601 UTC timestamp")


class DocumentUploadResponse(BaseModel):
    """Response model for POST /documents/upload endpoint."""

    metadata: DocumentMetadataSchema = Field(..., description="Document metadata specification")
    chunks: List[DocumentChunkSchema] = Field(default_factory=list, description="Extracted document text chunks")
    status: str = Field(default="SUCCESS", description="Processing status indicator")
