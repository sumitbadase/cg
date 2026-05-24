"""Create graph nodes from parsed CPP query entities."""

from __future__ import annotations

from typing import Any


def create_cpp_nodes(parsed_query: dict[str, Any]) -> list[dict[str, Any]]:
    """Build graph node payloads from a parsed CPP query.

    Args:
        parsed_query: Output of ``CPPQueryParser.parse``.

    Returns:
        List of node dictionaries ready for graph upload.
    """
    # TODO: Map parsed entities (services, endpoints, tables) to graph node schemas
    nodes: list[dict[str, Any]] = []
    _ = parsed_query
    return nodes
