# AI Change Analyzer

AI-powered change analyzer for JIRA tickets, GitHub pull requests, and graph-based insights.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management

## Quick Start

```bash
# Install dependencies
uv sync

# Copy environment template and configure credentials
cp .env.example .env

# Run the API server
uv run uvicorn main:app --reload --app-dir src
```

The API will be available at `http://localhost:8000`. Interactive docs at `/docs`.

## Project Structure

```
src/
├── main.py              # FastAPI application entry point
├── entrypoints.py       # CLI and programmatic entry points
├── models.py            # Pydantic request/response models
├── pydantic_formats.py  # Custom Pydantic field types and validators
├── utils.py             # Shared utility helpers
├── scheduler.py         # Background job scheduling
├── exceptions.py        # Application-specific exceptions
├── jira/                # JIRA API client and data extraction
├── cpp/                 # CPP query parsing and node creation
├── prompts/             # LLM prompt templates for change analysis
├── graph/               # Graph database integration (Gremlin)
├── parsers/             # Base parser abstractions
└── github/              # GitHub PR fetching and change analysis

tests/
└── api/                 # API endpoint tests
```

## Development

```bash
# Run tests
uv run pytest

# Run with dev dependencies
uv sync --dev
```

## Docker

```bash
docker build -t ai-change-analyzer .
docker run -p 8000:8000 --env-file .env ai-change-analyzer
```

## Environment Variables

See [.env.example](.env.example) for all supported configuration options.
