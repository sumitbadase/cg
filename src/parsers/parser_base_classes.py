"""Base parser classes for change data normalization."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedChange:
    """Normalized representation of a change from any source."""

    source: str
    identifier: str
    title: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    affected_entities: list[str] = field(default_factory=list)


class BaseChangeParser(ABC):
    """Abstract base class for source-specific change parsers."""

    @abstractmethod
    def parse(self, raw_data: dict[str, Any]) -> ParsedChange:
        """Parse raw source data into a normalized ``ParsedChange``.

        Args:
            raw_data: Unprocessed payload from the source system.

        Returns:
            Normalized change record.
        """
        raise NotImplementedError

    @abstractmethod
    def supports(self, source: str) -> bool:
        """Return whether this parser handles the given source type.

        Args:
            source: Source identifier (e.g. ``jira``, ``github``).

        Returns:
            True if this parser can handle the source.
        """
        raise NotImplementedError
