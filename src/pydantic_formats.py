"""Custom Pydantic field types, validators, and API models."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, Field, StringConstraints

JiraIssueKey = Annotated[str, StringConstraints(pattern=r"^[A-Z][A-Z0-9]+-\d+$")]
GitHubRepoSlug = Annotated[str, StringConstraints(pattern=r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$")]
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class HealthStatus(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModel):
    status: HealthStatus = HealthStatus.OK
    service: str = "ai-change-analyzer"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AnalyzePRRequest(BaseModel):
    repository: GitHubRepoSlug
    pull_request_number: int = Field(ge=1)


class AnalyzePRWithCommentTargetRequest(AnalyzePRRequest):
    comment_target: NonEmptyStr
    line_number: int | None = Field(default=None, ge=1)


class CloneRepositoryRequest(BaseModel):
    repository: GitHubRepoSlug | None = None
    clone_url: NonEmptyStr | None = None
    target_directory: NonEmptyStr | None = None


class InitialFillReposRequest(BaseModel):
    organization: NonEmptyStr
    repositories: list[GitHubRepoSlug] = Field(default_factory=list)


class InitialFillPRsRequest(BaseModel):
    repository: GitHubRepoSlug
    since_days: int = Field(default=30, ge=1)


class InitialFillJiraRequest(BaseModel):
    project_key: NonEmptyStr
    since_days: int = Field(default=30, ge=1)


class LoadPRRequest(BaseModel):
    repository: GitHubRepoSlug
    pull_request_number: int = Field(ge=1)
    force_reload: bool = False


class GraphOperationResponse(BaseModel):
    status: str
    message: str
    nodes_dropped: int | None = None
    nodes_created: int | None = None


class OperationResponse(BaseModel):
    status: str
    message: str
    request_id: str | None = None
    data: dict[str, Any] | None = None


def normalize_repo_slug(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Repository slug must not be empty")
    return normalized
