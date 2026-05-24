"""Base class for graph database connectivity."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from exceptions import GraphDatabaseError


class GraphBase(ABC):
    """Abstract base for Gremlin-compatible graph database clients."""

    def __init__(self, url: str, username: str = "", password: str = "") -> None:
        """Initialize graph connection settings.

        Args:
            url: WebSocket URL for the Gremlin endpoint.
            username: Optional authentication username.
            password: Optional authentication password.
        """
        self.url = url
        self.username = username
        self.password = password
        self._connection: Any = None

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the graph database."""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the graph database connection."""
        raise NotImplementedError

    @abstractmethod
    async def execute(self, query: str, bindings: dict[str, Any] | None = None) -> Any:
        """Execute a Gremlin query.

        Args:
            query: Gremlin traversal string.
            bindings: Optional query parameter bindings.

        Returns:
            Query result payload.

        Raises:
            GraphDatabaseError: If execution fails.
        """
        raise NotImplementedError
