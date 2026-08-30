"""
Logging System Utility.

Provides reusable dual console and timestamped rotating file logging
for the Sovereign On-Premise Agentic AI Workbench.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from config.settings import settings

# Standard Log Formatter with Timestamp, Level, Logger Name, Module, and Line Number
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str = "workbench",
    log_level: Optional[str] = None,
    log_to_console: Optional[bool] = None,
    log_to_file: Optional[bool] = None,
) -> logging.Logger:
    """
    Constructs and configures a reusable Python logger with console and file handlers.

    :param name: Logger module identifier name
    :param log_level: Logging severity level (overrides settings if provided)
    :param log_to_console: Whether to emit console logs (overrides settings if provided)
    :param log_to_file: Whether to write persistent file logs (overrides settings if provided)
    :return: Fully configured logging.Logger instance
    """
    logger = logging.getLogger(name)

    # Determine configuration parameters
    level_str = log_level or settings.LOG_LEVEL
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # 1. Console Handler Setup
    should_log_console = log_to_console if log_to_console is not None else settings.LOG_TO_CONSOLE
    if should_log_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 2. File Handler Setup
    should_log_file = log_to_file if log_to_file is not None else settings.LOG_TO_FILE
    if should_log_file:
        log_dir = Path(settings.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_filepath = log_dir / "workbench.log"

        file_handler = RotatingFileHandler(
            filename=log_filepath,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger to eliminate duplicate lines
    logger.propagate = False

    return logger


# Default Workbench Global Logger Singleton
logger = setup_logger("workbench")
