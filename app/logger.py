"""Logging setup for the calculator application."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

_LOGGER_NAME = "calculator"
_configured = False


def setup_logging(log_file: Path, encoding: str = "utf-8") -> logging.Logger:
    """
    Configure application logging to write to the given file.

    Safe to call multiple times; subsequent calls reuse the existing logger.
    """
    global _configured

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    if not _configured:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding=encoding)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Output warnings and errors to console as well
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.WARNING)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        _configured = True

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return the application logger or a child logger."""
    if name:
        return logging.getLogger(f"{_LOGGER_NAME}.{name}")
    return logging.getLogger(_LOGGER_NAME)


def reset_logging_for_tests() -> None:  # pragma: no cover
    """Reset logging state between tests."""
    global _configured
    logger = logging.getLogger(_LOGGER_NAME)
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
    _configured = False
