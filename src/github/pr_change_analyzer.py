"""Analyze pull request changes for impact and risk."""

from __future__ import annotations

from typing import Any

from github.git_pr_fetcher import GitPRFetcher
from parsers.parser_base_classes import ParsedChange


class PRChangeAnalyzer:
    """Analyze GitHub PR diffs and produce normalized change records."""

    def __init__(self, fetcher: GitPRFetcher) -> None:
        """Initialize the PR change analyzer.

        Args:
            fetcher: Configured ``GitPRFetcher`` instance.
        """
        self.fetcher = fetcher

    async def analyze(self, repo: str, pr_number: int) -> ParsedChange:
        """Analyze a pull request and return a normalized change record.

        Args:
            repo: Repository slug in ``owner/name`` format.
            pr_number: Pull request number.

        Returns:
            ``ParsedChange`` with title, description, and affected file paths.
        """
        # TODO: Classify file changes by type (config, API, schema) and score risk
        pr = await self.fetcher.fetch_pr(repo, pr_number)
        files = await self.fetcher.fetch_pr_files(repo, pr_number)
        affected = [f.get("filename", "") for f in files if f.get("filename")]

        return ParsedChange(
            source="github",
            identifier=f"{repo}#{pr_number}",
            title=pr.get("title") or "",
            description="",
            metadata={"pr": pr, "file_count": len(files)},
            affected_entities=affected,
        )

    async def summarize_diff(self, repo: str, pr_number: int) -> dict[str, Any]:
        """Produce a concise diff summary suitable for LLM prompts.

        Args:
            repo: Repository slug.
            pr_number: Pull request number.

        Returns:
            Summary dictionary with changed files and line counts.
        """
        # TODO: Aggregate additions/deletions and highlight high-risk paths
        files = await self.fetcher.fetch_pr_files(repo, pr_number)
        return {
            "repo": repo,
            "pr_number": pr_number,
            "files_changed": len(files),
            "files": files,
        }
