"""Programmatic entry points invoked by the FastAPI routes."""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any

from loguru import logger

from dashboard.metrics_aggregator import build_dashboard_metrics
from exceptions import (
    ChangeAnalyzerError,
    ConfigurationError,
    GitHubClientError,
    GitRepositoryError,
    GraphDatabaseError,
    JiraClientError,
    ParserError,
)
from git_integration.git_client import GitClient
from parsers.git_repo_parser import parse_and_store_repository
from pydantic_formats import (
    AnalyzePRRequest,
    AnalyzePRWithCommentTargetRequest,
    CloneRepositoryRequest,
    DashboardMetricsResponse,
    GraphOperationResponse,
    HealthResponse,
    HealthStatus,
    InitialFillJiraRequest,
    InitialFillPRsRequest,
    InitialFillReposRequest,
    LoadPRRequest,
    OperationResponse,
    ParseRepositoryRequest,
    RepositoryInventoryResponse,
    normalize_repo_slug,
)
from utils import get_repo_storage_dir


def health_check() -> HealthResponse:
    logger.debug("Health check requested")
    return HealthResponse(status=HealthStatus.OK)


async def get_dashboard_metrics(repository_name: str) -> DashboardMetricsResponse:
    """Return code criticality, bug frequency, and CFUSA/FuSa dashboard metrics."""
    metrics = build_dashboard_metrics(repository_name)
    return DashboardMetricsResponse(**metrics)


def get_dashboard_html() -> str:
    """Load the CFUSA safety dashboard HTML template."""
    template_path = Path(__file__).resolve().parent / "dashboard" / "templates" / "dashboard.html"
    return template_path.read_text(encoding="utf-8")


async def analyze_pr(request: AnalyzePRRequest) -> OperationResponse:
    repo = normalize_repo_slug(request.repository)
    logger.info("Analyzing PR {}/{}", repo, request.pull_request_number)
    request_id = str(uuid.uuid4())
    return OperationResponse(
        status="accepted",
        message=f"PR analysis queued for {repo}#{request.pull_request_number}",
        request_id=request_id,
        data={"repository": repo, "pull_request_number": request.pull_request_number},
    )


async def analyze_pr_with_comment_target(
    request: AnalyzePRWithCommentTargetRequest,
) -> OperationResponse:
    repo = normalize_repo_slug(request.repository)
    logger.info(
        "Analyzing PR {}/{} for comment target {}",
        repo,
        request.pull_request_number,
        request.comment_target,
    )
    request_id = str(uuid.uuid4())
    return OperationResponse(
        status="accepted",
        message=f"Scoped PR analysis queued for {repo}#{request.pull_request_number}",
        request_id=request_id,
        data={
            "repository": repo,
            "pull_request_number": request.pull_request_number,
            "comment_target": request.comment_target,
            "line_number": request.line_number,
        },
    )


async def clone_repository(request: CloneRepositoryRequest) -> OperationResponse:
    if not request.repository and not request.clone_url:
        raise ConfigurationError("Provide either repository or clone_url")

    identifier = request.clone_url or normalize_repo_slug(request.repository or "")
    client = GitClient(base_dir=get_repo_storage_dir())
    local_path = await asyncio.to_thread(
        client.clone_or_pull,
        identifier,
        target_directory=request.target_directory,
    )
    metadata = await asyncio.to_thread(client.metadata, local_path)

    logger.info("Cloned or updated repository at {}", local_path)
    request_id = str(uuid.uuid4())
    return OperationResponse(
        status="completed",
        message=f"Repository available at {local_path}",
        request_id=request_id,
        data={
            "repository": request.repository,
            "clone_url": request.clone_url,
            "local_path": str(local_path),
            **metadata,
        },
    )


async def parse_repository(request: ParseRepositoryRequest) -> RepositoryInventoryResponse:
    """Clone or open a repository, scan it, and store inventory artifacts."""
    repo_path = await _resolve_repository_path(request)
    summary = await asyncio.to_thread(
        parse_and_store_repository,
        repo_path,
        max_files=request.max_files,
        store_inventory=request.store_inventory,
    )
    return RepositoryInventoryResponse(
        status="completed",
        message=f"Repository inventory built for {summary['repository_name']}",
        repository_name=summary["repository_name"],
        local_path=summary["local_path"],
        head_commit=summary["head_commit"],
        active_branch=summary["active_branch"],
        file_count=summary["file_count"],
        directory_count=summary["directory_count"],
        node_count=summary["node_count"],
        edge_count=summary["edge_count"],
        inventory_path=summary["inventory_path"],
    )


async def _resolve_repository_path(request: ParseRepositoryRequest) -> Path:
    if request.repository_path:
        path = Path(request.repository_path)
        if not path.exists():
            raise GitRepositoryError(f"Repository path does not exist: {path}")
        return path

    if not request.repository and not request.clone_url:
        raise ConfigurationError("Provide repository_path, repository, or clone_url")

    identifier = request.clone_url or normalize_repo_slug(request.repository or "")
    client = GitClient(base_dir=get_repo_storage_dir())
    return await asyncio.to_thread(
        client.clone_or_pull,
        identifier,
        target_directory=request.target_directory,
        depth=request.shallow_depth,
    )


async def initial_fill_repos(request: InitialFillReposRequest) -> OperationResponse:
    logger.info("Initial fill repos for org {}", request.organization)
    request_id = str(uuid.uuid4())
    return OperationResponse(
        status="accepted",
        message=f"Repository backfill queued for {request.organization}",
        request_id=request_id,
        data={"organization": request.organization, "repositories": request.repositories},
    )


async def initial_fill_prs(request: InitialFillPRsRequest) -> OperationResponse:
    repo = normalize_repo_slug(request.repository)
    logger.info("Initial fill PRs for {}", repo)
    request_id = str(uuid.uuid4())
    return OperationResponse(
        status="accepted",
        message=f"PR backfill queued for {repo}",
        request_id=request_id,
        data={"repository": repo, "since_days": request.since_days},
    )


async def initial_fill_jira(request: InitialFillJiraRequest) -> OperationResponse:
    logger.info("Initial fill JIRA for project {}", request.project_key)
    request_id = str(uuid.uuid4())
    return OperationResponse(
        status="accepted",
        message=f"JIRA backfill queued for project {request.project_key}",
        request_id=request_id,
        data={"project_key": request.project_key, "since_days": request.since_days},
    )


async def load_pr(request: LoadPRRequest) -> OperationResponse:
    repo = normalize_repo_slug(request.repository)
    logger.info("Loading PR {}/{}", repo, request.pull_request_number)
    request_id = str(uuid.uuid4())
    return OperationResponse(
        status="accepted",
        message=f"PR load queued for {repo}#{request.pull_request_number}",
        request_id=request_id,
        data={
            "repository": repo,
            "pull_request_number": request.pull_request_number,
            "force_reload": request.force_reload,
        },
    )


async def drop_graph(*, confirm: bool = False) -> GraphOperationResponse:
    if not confirm:
        raise ConfigurationError("Set confirm=true to drop the graph")
    logger.warning("Dropping graph database")
    return GraphOperationResponse(status="completed", message="Graph dropped successfully", nodes_dropped=0)


async def recreate_graph() -> GraphOperationResponse:
    logger.info("Recreating graph database")
    return GraphOperationResponse(status="completed", message="Graph recreated successfully", nodes_created=0)


def map_exception_to_status(exc: ChangeAnalyzerError) -> int:
    mapping: dict[type[ChangeAnalyzerError], int] = {
        ConfigurationError: 400,
        ParserError: 422,
        GitRepositoryError: 400,
        JiraClientError: 502,
        GitHubClientError: 502,
        GraphDatabaseError: 503,
    }
    return mapping.get(type(exc), 500)


def error_detail(exc: ChangeAnalyzerError) -> dict[str, Any]:
    detail: dict[str, Any] = {"message": exc.message}
    if exc.details:
        detail["details"] = exc.details
    return detail
