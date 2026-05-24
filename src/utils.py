"""Shared utility helpers used across the application."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given module name.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        A standard library logger instance.
    """
    # TODO: Configure structured logging format and log level from settings
    return logging.getLogger(name)


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dictionaries.

    Args:
        data: Source dictionary.
        keys: Sequence of keys to traverse.
        default: Value returned when a key is missing.

    Returns:
        The nested value if found, otherwise ``default``.
    """
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
