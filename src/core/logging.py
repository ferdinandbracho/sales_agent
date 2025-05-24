"""
Simple logging configuration using Python's standard logging module.
"""

import logging
import logging.handlers
from pathlib import Path

from src.config import settings


def setup_logging() -> None:
    """
    Configure logging for the application using settings from config.
    """
    log_config = settings.logging

    # Create log directory if it doesn't exist
    log_path = Path(log_config.LOG_DIR) / log_config.LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_config.LOG_LEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_config.LOG_LEVEL}")

    # Define log format
    formatter = logging.Formatter(log_config.LOG_FORMAT)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=log_config.MAX_BYTES,
        backupCount=log_config.BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Configure log levels for external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger.info("Logging configured successfully")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Name of the logger (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Create a default logger
log = get_logger(__name__)
