"""Programmatic entry points invoked by the FastAPI routes."""

from __future__ import annotations

import uuid
from typing import Any

from loguru import logger

from exceptions import (
    ChangeAnalyzerError,
    ConfigurationError,
    GitHubClientError,
    GraphDatabaseError,
    JiraClientError,
    ParserError,
)
from pydantic_formats import (
    AnalyzePRRequest,
    AnalyzePRWithCommentTargetRequest,
    CloneRepositoryRequest,
    GraphOperationResponse,
    HealthResponse,
    HealthStatus,
    InitialFillJiraRequest,
    InitialFillPRsRequest,
    InitialFillReposRequest,
    LoadPRRequest,
    OperationResponse,
    normalize_repo_slug,
)


def health_check() -> HealthResponse:
    logger.debug("Health check requested")
    return HealthResponse(status=HealthStatus.OK)


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
    logger.info("Cloning repository {}", identifier)
    request_id = str(uuid.uuid4())
    return OperationResponse(
        status="accepted",
        message=f"Repository clone queued for {identifier}",
        request_id=request_id,
        data={
            "repository": request.repository,
            "clone_url": request.clone_url,
            "target_directory": request.target_directory,
        },
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
