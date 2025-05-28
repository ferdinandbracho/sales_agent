"""
Logging configuration using Python's standard logging module with file rotation.

This module provides a centralized logging configuration that:
- Logs to both console and file
- Rotates log files when they reach 10MB
- Keeps up to 3 backup log files
- Uses a consistent log format with timestamps and source information
"""

import logging
import logging.handlers
import os
from pathlib import Path

from src.config import settings

# Global flag to track if logging is initialized
_logging_initialized = False


def setup_logging() -> None:
    """
    Configure logging for the application using settings from config.

    This function:
    - Creates the log directory if it doesn't exist
    - Sets up console and file logging with rotation
    - Configures log levels for both root and third-party loggers
    - Ensures the function is idempotent (can be called multiple times safely)
    """
    global _logging_initialized

    # Only initialize logging once
    if _logging_initialized:
        return

    try:
        log_config = settings.logging

        # Create log directory if it doesn't exist
        log_dir = Path(log_config.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / log_config.LOG_FILE

        # Ensure the log directory is writable
        if not os.access(log_dir, os.W_OK):
            raise PermissionError(f"Cannot write to log directory: {log_dir}")

        # Convert string log level to logging constant
        numeric_level = getattr(logging, log_config.LOG_LEVEL.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {log_config.LOG_LEVEL}")

        # Define log format
        formatter = logging.Formatter(log_config.LOG_FORMAT)

        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(numeric_level)

        # Remove any existing handlers to avoid duplicate logs
        for handler in logger.handlers[:]:
            handler.close()
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

        # Configure log levels for external libraries to reduce noise
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)

        logger.info("Logging configured successfully")
        logger.info(f"Log file: {log_path.absolute()}")
        logger.debug(f"Log level set to: {log_config.LOG_LEVEL}")

        _logging_initialized = True

    except Exception as e:
        # If we can't set up file logging, at least log to console
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to configure logging: {e}")
        logging.error("Falling back to basic console logging")
        _logging_initialized = (
            True  # Still mark as initialized to prevent repeated errors
        )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    This function ensures that logging is configured before returning a logger.
    It's safe to call this at module level.

    Args:
        name: Name of the logger (usually __name__)

    Returns:
        Configured logger instance
    """
    setup_logging()  # Ensure logging is configured
    return logging.getLogger(name)


# Create a default logger that can be imported and used directly
log = get_logger(__name__)

# Initialize logging when this module is imported
setup_logging()
