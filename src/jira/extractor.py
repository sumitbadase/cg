"""Extract structured change data from JIRA issue payloads."""

from __future__ import annotations

from typing import Any

from jira.client import JiraClient


class JiraExtractor:
    """Transform raw JIRA API responses into normalized change records."""

    def __init__(self, client: JiraClient) -> None:
        """Initialize the extractor with a JIRA client.

        Args:
            client: Configured ``JiraClient`` instance.
        """
        self.client = client

    async def extract_issue_summary(self, issue_key: str) -> dict[str, Any]:
        """Extract summary fields from a JIRA issue.

        Args:
            issue_key: JIRA issue key.

        Returns:
            Normalized dictionary with key, summary, status, assignee, and labels.
        """
        # TODO: Fetch issue via client and map fields to normalized schema
        _ = await self.client.get_issue(issue_key)
        return {
            "issue_key": issue_key,
            "summary": None,
            "status": None,
            "assignee": None,
            "labels": [],
        }
