"""Fetch GitHub pull request metadata and diffs."""

from __future__ import annotations

from typing import Any

from github.github_helpers import GitHubHelpers


class GitPRFetcher:
    """Retrieve pull request details and file changes from GitHub."""

    def __init__(self, helpers: GitHubHelpers) -> None:
        """Initialize the PR fetcher.

        Args:
            helpers: Configured ``GitHubHelpers`` instance.
        """
        self.helpers = helpers

    async def fetch_pr(self, repo: str, pr_number: int) -> dict[str, Any]:
        """Fetch pull request metadata.

        Args:
            repo: Repository slug in ``owner/name`` format.
            pr_number: Pull request number.

        Returns:
            Normalized PR metadata dictionary.
        """
        # TODO: GET /repos/{owner}/{repo}/pulls/{pull_number}
        path = f"/repos/{repo}/pulls/{pr_number}"
        data = await self.helpers.get(path)
        return {
            "repo": repo,
            "number": pr_number,
            "title": data.get("title"),
            "state": data.get("state"),
            "author": (data.get("user") or {}).get("login"),
        }

    async def fetch_pr_files(self, repo: str, pr_number: int) -> list[dict[str, Any]]:
        """Fetch the list of files changed in a pull request.

        Args:
            repo: Repository slug in ``owner/name`` format.
            pr_number: Pull request number.

        Returns:
            List of file change records with filename, status, and patch.
        """
        # TODO: Paginate GET /repos/{owner}/{repo}/pulls/{pull_number}/files
        path = f"/repos/{repo}/pulls/{pr_number}/files"
        files = await self.helpers.get(path)
        return files if isinstance(files, list) else []
