"""
Path Security & Document Upload Hardening Module.
"""

import os
import re
from pathlib import Path
from typing import Set

ALLOWED_EXTENSIONS: Set[str] = {
    ".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx", ".png", ".jpg", ".jpeg"
}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize upload filename to prevent path traversal attack vectors.
    Strips directory separators, relative paths (..), and invalid characters.
    """
    if not filename:
        return "unnamed_document.txt"

    # Extract basename only
    clean_name = os.path.basename(filename)
    clean_name = os.path.basename(clean_name.replace("\\", "/"))

    # Remove relative path traversal tokens
    clean_name = clean_name.replace("..", "").replace("/", "").replace("\\", "")

    # Retain alphanumeric characters, dots, dashes, underscores
    clean_name = re.sub(r"[^a-zA-Z0-9._\-]", "_", clean_name)

    if not clean_name:
        return "unnamed_document.txt"

    return clean_name


def validate_upload_file(
    filename: str,
    file_bytes: bytes,
    max_size_bytes: int = 50 * 1024 * 1024,
) -> None:
    """
    Validate file upload properties against security thresholds.
    Raises ValueError on invalid path traversal, extension, or size.
    """
    # 1. Path traversal check
    if ".." in filename or "/" in filename or "\\" in filename or ":" in filename:
        clean = sanitize_filename(filename)
        if clean != filename:
            raise ValueError(f"Path traversal sequence detected in filename '{filename}'.")

    # 2. Extension check
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File extension '{ext}' is not permitted. Allowed: {sorted(list(ALLOWED_EXTENSIONS))}")

    # 3. Empty file check
    if len(file_bytes) == 0:
        raise ValueError("File content is empty (0 bytes). Upload rejected.")

    # 4. Maximum size check
    if len(file_bytes) > max_size_bytes:
        raise ValueError(
            f"File size ({len(file_bytes)} bytes) exceeds maximum limit ({max_size_bytes} bytes)."
        )


def resolve_safe_path(base_dir: Path, filename: str) -> Path:
    """
    Resolve target path securely within base directory, ensuring no path traversal escapes.
    """
    clean_name = sanitize_filename(filename)
    target_path = (base_dir / clean_name).resolve()

    # Ensure target path is strictly contained inside base_dir
    base_resolved = base_dir.resolve()
    if not str(target_path).startswith(str(base_resolved)):
        raise ValueError(f"Target path '{target_path}' escapes base directory '{base_dir}'.")

    return target_path
