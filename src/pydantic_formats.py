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


class ParseRepositoryRequest(BaseModel):
    """Request payload for parsing a local or remote git repository."""

    repository: GitHubRepoSlug | None = None
    clone_url: NonEmptyStr | None = None
    repository_path: NonEmptyStr | None = None
    target_directory: NonEmptyStr | None = None
    max_files: int | None = Field(default=None, ge=1)
    store_inventory: bool = True
    shallow_depth: int | None = Field(default=1, ge=1)


class RepositoryInventoryResponse(BaseModel):
    """Response payload for repository parse/inventory operations."""

    status: str
    message: str
    repository_name: str
    local_path: str
    head_commit: str
    active_branch: str
    file_count: int
    directory_count: int
    node_count: int
    edge_count: int
    inventory_path: str | None = None


class OperationResponse(BaseModel):
    status: str
    message: str
    request_id: str | None = None
    data: dict[str, Any] | None = None


class DashboardMetricsResponse(BaseModel):
    """Dashboard payload for code criticality, bug frequency, and FuSa metrics."""

    generated_at: str
    repository_name: str
    head_commit: str | None = None
    file_count: int
    criticality: dict[str, Any]
    bug_frequency: dict[str, Any]
    functional_safety: dict[str, Any]
    cfusa_dashboard: dict[str, Any]


def normalize_repo_slug(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Repository slug must not be empty")
    return normalized
