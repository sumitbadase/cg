"""JIRA REST API client."""

from __future__ import annotations

from typing import Any

import httpx

from exceptions import JiraClientError


class JiraClient:
    """HTTP client for interacting with the JIRA REST API."""

    def __init__(self, base_url: str, email: str, api_token: str) -> None:
        """Initialize the JIRA client.

        Args:
            base_url: JIRA instance base URL.
            email: Account email for basic auth.
            api_token: JIRA API token.
        """
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            auth=(email, api_token),
            headers={"Accept": "application/json"},
            timeout=30.0,
        )

    async def get_issue(self, issue_key: str) -> dict[str, Any]:
        """Fetch a JIRA issue by key.

        Args:
            issue_key: JIRA issue key (e.g. ``PROJ-123``).

        Returns:
            Parsed issue payload from the JIRA API.

        Raises:
            JiraClientError: If the request fails.
        """
        # TODO: Implement GET /rest/api/3/issue/{issueKey}
        raise JiraClientError(f"Not implemented: get_issue({issue_key})")

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
