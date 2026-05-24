"""FastAPI application entry point for ai-change-analyzer."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Awaitable, Callable, TypeVar

from fastapi import FastAPI, HTTPException, Query, status
from loguru import logger

import entrypoints
from exceptions import ChangeAnalyzerError
from pydantic_formats import (
    AnalyzePRRequest,
    AnalyzePRWithCommentTargetRequest,
    CloneRepositoryRequest,
    GraphOperationResponse,
    HealthResponse,
    InitialFillJiraRequest,
    InitialFillPRsRequest,
    InitialFillReposRequest,
    LoadPRRequest,
    OperationResponse,
)
from scheduler import create_scheduler, shutdown_scheduler, start_scheduler

T = TypeVar("T")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting ai-change-analyzer")
    scheduler = create_scheduler()
    start_scheduler(scheduler)
    app.state.scheduler = scheduler
    yield
    shutdown_scheduler(scheduler)
    logger.info("Stopped ai-change-analyzer")


app = FastAPI(
    title="AI Change Analyzer",
    description="Analyze JIRA tickets, GitHub PRs, and graph relationships for change impact.",
    version="0.1.0",
    lifespan=lifespan,
)


async def _invoke(handler: Callable[..., Awaitable[T]], *args: object, **kwargs: object) -> T:
    try:
        return await handler(*args, **kwargs)
    except ChangeAnalyzerError as exc:
        status_code = entrypoints.map_exception_to_status(exc)
        logger.error("{}: {}", type(exc).__name__, exc.message)
        raise HTTPException(status_code=status_code, detail=entrypoints.error_detail(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error in {}", handler.__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        ) from exc


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def get_health() -> HealthResponse:
    return entrypoints.health_check()


@app.post("/analyze-pr", response_model=OperationResponse, status_code=status.HTTP_202_ACCEPTED, tags=["analysis"])
async def post_analyze_pr(request: AnalyzePRRequest) -> OperationResponse:
    return await _invoke(entrypoints.analyze_pr, request)


@app.post("/analyze-pr-with-comment-target", response_model=OperationResponse, status_code=status.HTTP_202_ACCEPTED, tags=["analysis"])
async def post_analyze_pr_with_comment_target(request: AnalyzePRWithCommentTargetRequest) -> OperationResponse:
    return await _invoke(entrypoints.analyze_pr_with_comment_target, request)


@app.post("/clone-repository", response_model=OperationResponse, status_code=status.HTTP_202_ACCEPTED, tags=["github"])
async def post_clone_repository(request: CloneRepositoryRequest) -> OperationResponse:
    return await _invoke(entrypoints.clone_repository, request)


@app.post("/initial-fill-repos", response_model=OperationResponse, status_code=status.HTTP_202_ACCEPTED, tags=["backfill"])
async def post_initial_fill_repos(request: InitialFillReposRequest) -> OperationResponse:
    return await _invoke(entrypoints.initial_fill_repos, request)


@app.post("/initial-fill-prs", response_model=OperationResponse, status_code=status.HTTP_202_ACCEPTED, tags=["backfill"])
async def post_initial_fill_prs(request: InitialFillPRsRequest) -> OperationResponse:
    return await _invoke(entrypoints.initial_fill_prs, request)


@app.post("/initial-fill-jira", response_model=OperationResponse, status_code=status.HTTP_202_ACCEPTED, tags=["backfill"])
async def post_initial_fill_jira(request: InitialFillJiraRequest) -> OperationResponse:
    return await _invoke(entrypoints.initial_fill_jira, request)


@app.post("/load-pr", response_model=OperationResponse, status_code=status.HTTP_202_ACCEPTED, tags=["github"])
async def post_load_pr(request: LoadPRRequest) -> OperationResponse:
    return await _invoke(entrypoints.load_pr, request)


@app.delete("/drop-graph", response_model=GraphOperationResponse, tags=["graph"])
async def delete_drop_graph(confirm: bool = Query(default=False)) -> GraphOperationResponse:
    return await _invoke(entrypoints.drop_graph, confirm=confirm)


@app.post("/recreate-graph", response_model=GraphOperationResponse, tags=["graph"])
async def post_recreate_graph() -> GraphOperationResponse:
    return await _invoke(entrypoints.recreate_graph)
