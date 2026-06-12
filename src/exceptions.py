"""Application-specific exception hierarchy."""

from __future__ import annotations


class ChangeAnalyzerError(Exception):
    """Base exception for all ai-change-analyzer errors."""

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(ChangeAnalyzerError):
    """Raised when required configuration is missing or invalid."""


class JiraClientError(ChangeAnalyzerError):
    """Raised when JIRA API operations fail."""


class GitHubClientError(ChangeAnalyzerError):
    """Raised when GitHub API operations fail."""


class GitRepositoryError(ChangeAnalyzerError):
    """Raised when local git clone, pull, or parse operations fail."""


class GraphDatabaseError(ChangeAnalyzerError):
    """Raised when graph database operations fail."""


class ParserError(ChangeAnalyzerError):
    """Raised when parsing change data fails."""


class SchedulerError(ChangeAnalyzerError):
    """Raised when background scheduler operations fail."""
