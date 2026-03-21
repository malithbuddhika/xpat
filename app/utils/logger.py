"""Logging utilities.

This module configures loguru to log to both console and a rotating file.
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from .config import LOG_DIR


def setup_logger() -> None:
    """Configure loguru logger."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "app.log"

    # Remove all default handlers, then add our own
    logger.remove()

    # Console handler
    logger.add(
        sys.stderr,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <7}</level> | <cyan>{message}</cyan>",
        level="INFO",
    )

    # Rotating file handler
    logger.add(
        str(log_path),
        rotation="10 MB",
        retention="14 days",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG",
    )


def get_logger() -> "loguru.Logger":
    return logger
