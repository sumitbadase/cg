"""Dashboard metrics tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from git import Repo

from dashboard.criticality_scorer import score_file_criticality, summarize_criticality
from dashboard.metrics_aggregator import build_dashboard_metrics
from dashboard.safety_classifier import classify_functional_safety, summarize_safety_metrics
from git_integration.inventory_builder import build_inventory_graph
from git_integration.inventory_store import InventoryStore
from git_integration.repo_scanner import RepoScanner
from git_integration.git_client import GitClient
from main import app


@pytest.fixture
def parsed_inventory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    inventory_dir = tmp_path / "inventories"
    monkeypatch.setenv("INVENTORY_STORAGE_DIR", str(inventory_dir))

    repo_path = tmp_path / "safety-repo"
    (repo_path / "drivers" / "brake").mkdir(parents=True)
    (repo_path / "drivers" / "brake" / "control.c").write_text("c" * 5000, encoding="utf-8")
    (repo_path / "docs").mkdir(parents=True, exist_ok=True)
    (repo_path / "docs" / "readme.md").write_text("# docs", encoding="utf-8")

    Repo.init(repo_path)
    repo = Repo(repo_path)
    repo.index.add(["drivers/brake/control.c", "docs/readme.md"])
    repo.index.commit("init")

    scanner = RepoScanner(git_client=GitClient(base_dir=tmp_path))
    inventory = scanner.scan(repo_path)
    nodes, edges = build_inventory_graph(inventory)
    InventoryStore(inventory_dir).save(inventory, nodes, edges)
    return inventory.repository_name


def test_criticality_scorer_flags_safety_paths() -> None:
    score = score_file_criticality(
        {"path": "drivers/brake/control.c", "extension": ".c", "size_bytes": 12000}
    )
    assert score["level"] in {"high", "critical"}
    assert score["score"] >= 50


def test_build_dashboard_metrics(parsed_inventory: str) -> None:
    metrics = build_dashboard_metrics(parsed_inventory)

    assert metrics["repository_name"] == parsed_inventory
    assert metrics["criticality"]["distribution"]["high"] + metrics["criticality"]["distribution"]["critical"] >= 1
    assert "asil_distribution" in metrics["functional_safety"]
    assert metrics["cfusa_dashboard"]["readiness_score"] >= 0


def test_dashboard_api_endpoints(parsed_inventory: str) -> None:
    client = TestClient(app)

    page = client.get("/dashboard")
    assert page.status_code == 200
    assert "CFUSA Safety Dashboard" in page.text

    response = client.get(f"/dashboard/metrics?repository_name={parsed_inventory}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["bug_frequency"]["total_bugs"] >= 0
    assert payload["functional_safety"]["files_requiring_safety_review"] >= 1


def test_safety_classifier_summary() -> None:
    records = [
        classify_functional_safety({"path": "drivers/brake/control.c"}, 85),
        classify_functional_safety({"path": "docs/readme.md"}, 5),
    ]
    summary = summarize_safety_metrics(records)
    assert summary["asil_distribution"]["ASIL-D"] >= 1
    assert summary["cfusa_readiness_score"] <= 100
