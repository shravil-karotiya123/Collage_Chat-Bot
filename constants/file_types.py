"""
Supported File Types, Extensions, and MIME Type Definitions.

Defines supported document, image, data, and output file specifications for the Workbench.
"""

from enum import Enum
from typing import Dict, Set


class DocumentCategory(str, Enum):
    """Categorization of supported input/output document types."""

    PDF = "pdf"
    EXCEL = "excel"
    WORD = "word"
    IMAGE = "image"
    DATA = "data"
    CODE = "code"
    TEXT = "text"


# Extension Mappings to Document Categories
SUPPORTED_EXTENSIONS: Dict[str, DocumentCategory] = {
    # PDF Files
    ".pdf": DocumentCategory.PDF,
    # Excel Files
    ".xlsx": DocumentCategory.EXCEL,
    ".xls": DocumentCategory.EXCEL,
    ".csv": DocumentCategory.DATA,
    # Word Files
    ".docx": DocumentCategory.WORD,
    ".doc": DocumentCategory.WORD,
    # Vision / Image Files
    ".png": DocumentCategory.IMAGE,
    ".jpg": DocumentCategory.IMAGE,
    ".jpeg": DocumentCategory.IMAGE,
    ".webp": DocumentCategory.IMAGE,
    ".bmp": DocumentCategory.IMAGE,
    ".tiff": DocumentCategory.IMAGE,
    # Structured Data
    ".json": DocumentCategory.DATA,
    ".yaml": DocumentCategory.DATA,
    ".yml": DocumentCategory.DATA,
    # Code Files
    ".py": DocumentCategory.CODE,
    ".sql": DocumentCategory.CODE,
    # Plain Text
    ".txt": DocumentCategory.TEXT,
    ".md": DocumentCategory.TEXT,
}

# MIME Types Dictionary
MIME_TYPES: Dict[str, str] = {
    ".pdf": "application/pdf",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".csv": "text/csv",
    ".json": "application/json",
    ".txt": "text/plain",
}

# Sets of Allowed Extensions for Easy Validation
ALLOWED_INPUT_EXTENSIONS: Set[str] = set(SUPPORTED_EXTENSIONS.keys())
ALLOWED_VISION_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
ALLOWED_DOCUMENT_EXTENSIONS: Set[str] = {".pdf", ".docx", ".doc", ".txt", ".md"}
ALLOWED_SPREADSHEET_EXTENSIONS: Set[str] = {".xlsx", ".xls", ".csv"}
