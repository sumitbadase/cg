"""Shared utility helpers used across the application."""

from __future__ import annotations

import logging
import os
from pathlib import Path
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


def get_repo_storage_dir() -> Path:
    """Return the local directory used for cloned git repositories."""
    return Path(os.getenv("REPO_STORAGE_DIR", "data/repos")).resolve()


def get_inventory_storage_dir() -> Path:
    """Return the local directory used for saved repository inventories."""
    return Path(os.getenv("INVENTORY_STORAGE_DIR", "data/inventories")).resolve()


def get_bug_storage_dir() -> Path:
    """Return the local directory used for repository bug record files."""
    path = Path(os.getenv("BUG_STORAGE_DIR", "data/bugs")).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path
