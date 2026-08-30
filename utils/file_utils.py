"""
File System Utilities.

Provides secure path resolution, file extension checking, directory creation,
and file size validation utilities.
"""

import os
from pathlib import Path
from typing import List, Union

from constants.file_types import ALLOWED_INPUT_EXTENSIONS, SUPPORTED_EXTENSIONS, DocumentCategory
from utils.logger import logger


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensures that a directory exists, creating all parent directories if necessary.

    :param directory_path: Path to target directory
    :return: Path object of validated directory
    """
    path = Path(directory_path).resolve()
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {path}")
    return path


def get_file_extension(filepath: Union[str, Path]) -> str:
    """
    Extracts normalized lower-case file extension from a file path.

    :param filepath: Path or filename string
    :return: Extension including leading dot (e.g., '.pdf')
    """
    return Path(filepath).suffix.lower()


def is_allowed_file_extension(filepath: Union[str, Path]) -> bool:
    """
    Checks if a file extension is in the supported extension catalog.

    :param filepath: Path or filename string
    :return: True if extension is supported, False otherwise
    """
    ext = get_file_extension(filepath)
    return ext in ALLOWED_INPUT_EXTENSIONS


def get_document_category(filepath: Union[str, Path]) -> DocumentCategory:
    """
    Determines the document category for a given file.

    :param filepath: Path or filename string
    :return: DocumentCategory enum value
    :raises ValueError: If extension is unsupported
    """
    ext = get_file_extension(filepath)
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: '{ext}' for file '{filepath}'")
    return SUPPORTED_EXTENSIONS[ext]


def get_file_size_bytes(filepath: Union[str, Path]) -> int:
    """
    Returns file size in bytes safely.

    :param filepath: Target file path
    :return: Size in bytes
    """
    path = Path(filepath).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    return path.stat().st_size


def list_files_in_directory(
    directory_path: Union[str, Path], extensions: List[str] = None
) -> List[Path]:
    """
    Lists files in a target directory, optionally filtered by extension.

    :param directory_path: Directory path to scan
    :param extensions: Optional list of extensions to filter (e.g. ['.pdf', '.xlsx'])
    :return: List of file Path objects
    """
    dir_path = Path(directory_path).resolve()
    if not dir_path.is_dir():
        logger.warning(f"Target directory does not exist: {dir_path}")
        return []

    files = [f for f in dir_path.iterdir() if f.is_file()]
    if extensions:
        normalized_exts = {e.lower() for e in extensions}
        files = [f for f in files if f.suffix.lower() in normalized_exts]
    return sorted(files)
