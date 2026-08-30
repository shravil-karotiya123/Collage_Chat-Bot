"""
Input & Environment Validation Utilities.

Provides sanitization, boundary checks, and system environment verification functions.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from config.settings import settings
from utils.logger import logger


def validate_environment() -> Tuple[bool, List[str]]:
    """
    Validates essential environment settings, storage directories, and system paths.

    :return: Tuple (is_valid: bool, issues: List[str])
    """
    issues: List[str] = []

    # Verify key data directory write access
    required_dirs = [
        settings.LOG_DIR,
        settings.DOCUMENT_DIR,
        settings.OUTPUT_DIR,
        settings.DATABASE_DIR,
        settings.VECTOR_STORE_DIR,
        settings.CACHE_DIR,
        settings.DOWNLOAD_DIR,
    ]

    for dir_path in required_dirs:
        try:
            p = Path(dir_path).resolve()
            p.mkdir(parents=True, exist_ok=True)
            # Test write access
            test_file = p / ".permissions_check"
            test_file.touch(exist_ok=True)
            test_file.unlink(missing_ok=True)
        except Exception as err:
            issues.append(f"Directory access check failed for '{dir_path}': {err}")

    # Validate memory constraints reasonable bounds
    if settings.MAX_VRAM_USAGE_MB > 16384:
        issues.append(f"MAX_VRAM_USAGE_MB ({settings.MAX_VRAM_USAGE_MB}) exceeds RTX 5050 hardware target.")

    if settings.MAX_RAM_USAGE_MB > 16384:
        issues.append(f"MAX_RAM_USAGE_MB ({settings.MAX_RAM_USAGE_MB}) exceeds 16 GB system memory setup.")

    is_valid = len(issues) == 0
    if not is_valid:
        logger.warning(f"Environment validation completed with {len(issues)} issue(s).")
    else:
        logger.info("Environment validation succeeded. All storage directories accessible.")

    return is_valid, issues


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes user input filenames to prevent path traversal vulnerabilities.

    :param filename: Base filename string
    :return: Safe sanitized filename string
    """
    cleaned = Path(filename).name
    # Strip null bytes and problematic special characters
    invalid_chars = '<>:"/\\|?*\0'
    for char in invalid_chars:
        cleaned = cleaned.replace(char, "_")
    return cleaned.strip()
