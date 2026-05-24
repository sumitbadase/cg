"""Gremlin query builders for the change impact graph."""

from __future__ import annotations


class GremlinQueries:
    """Factory for parameterized Gremlin traversal strings."""

    def downstream_services(self, service_name: str) -> str:
        """Build a query to find downstream services from a given service.

        Args:
            service_name: Source service name binding.

        Returns:
            Gremlin query string with ``serviceName`` binding placeholder.
        """
        # TODO: Implement multi-hop DEPENDS_ON traversal
        return (
            "g.V().has('service', 'name', serviceName)"
            ".repeat(out('DEPENDS_ON')).emit()"
            ".values('name')"
        )

    def entity_neighbors(self, entity_id: str, hops: int = 2) -> str:
        """Build a query to fetch neighbors within N hops of an entity.

        Args:
            entity_id: Starting vertex business key.
            hops: Maximum traversal depth.

        Returns:
            Gremlin query string.
        """
        # TODO: Parameterize hop count and edge labels
        _ = hops
        return (
            "g.V().has('entity', 'id', entityId)"
            ".repeat(both()).times(hops).dedup()"
        )
