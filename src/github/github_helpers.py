"""Shared helpers for GitHub API interactions."""

from __future__ import annotations

from typing import Any

import httpx

from exceptions import GitHubClientError


class GitHubHelpers:
    """Utility methods for authenticated GitHub REST API calls."""

    def __init__(self, token: str, base_url: str = "https://api.github.com") -> None:
        """Initialize GitHub helpers.

        Args:
            token: GitHub personal access token or app token.
            base_url: GitHub API base URL (supports GitHub Enterprise).
        """
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=30.0,
        )

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Perform an authenticated GET request to the GitHub API.

        Args:
            path: API path relative to the base URL.
            params: Optional query parameters.

        Returns:
            Parsed JSON response body.

        Raises:
            GitHubClientError: If the request fails.
        """
        # TODO: Implement request with rate-limit handling and error mapping
        response = await self._client.get(path, params=params)
        if response.status_code >= 400:
            raise GitHubClientError(
                f"GitHub API error: {response.status_code}",
                details={"path": path, "body": response.text},
            )
        return response.json()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
