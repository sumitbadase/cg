"""Tests for local git repository integration."""

from __future__ import annotations

from pathlib import Path

import pytest
from git import Repo

from git_integration.git_client import GitClient
from git_integration.inventory_builder import build_inventory_graph
from git_integration.inventory_store import InventoryStore
from git_integration.repo_scanner import RepoScanner
from parsers.git_repo_parser import parse_and_store_repository


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    repo_path = tmp_path / "sample-repo"
    repo_path.mkdir()
    (repo_path / "src").mkdir()
    (repo_path / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (repo_path / "README.md").write_text("# sample\n", encoding="utf-8")
    Repo.init(repo_path)
    repo = Repo(repo_path)
    repo.index.add(["src/main.py", "README.md"])
    repo.index.commit("initial commit")
    return repo_path


def test_repo_scanner_builds_inventory(sample_repo: Path) -> None:
    scanner = RepoScanner(git_client=GitClient(base_dir=sample_repo.parent))
    inventory = scanner.scan(sample_repo)

    assert inventory.repository_name == "sample-repo"
    assert inventory.file_count == 2
    assert inventory.directory_count >= 1
    assert inventory.head_commit


def test_inventory_builder_creates_graph_payload(sample_repo: Path) -> None:
    scanner = RepoScanner(git_client=GitClient(base_dir=sample_repo.parent))
    inventory = scanner.scan(sample_repo)
    nodes, edges = build_inventory_graph(inventory)

    assert any(node["label"] == "Repository" for node in nodes)
    assert any(node["label"] == "File" for node in nodes)
    assert any(edge["label"] == "CONTAINS" for edge in edges)
    assert len(nodes) >= 3
    assert len(edges) >= 2


def test_parse_and_store_repository_writes_json(sample_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inventory_dir = sample_repo.parent / "inventories"
    monkeypatch.setenv("INVENTORY_STORAGE_DIR", str(inventory_dir))

    summary = parse_and_store_repository(sample_repo, store_inventory=True)

    assert summary["file_count"] == 2
    assert summary["node_count"] >= 3
    assert summary["inventory_path"] is not None
    assert Path(summary["inventory_path"]).exists()

    store = InventoryStore(inventory_dir)
    loaded = store.load("sample-repo")
    assert loaded is not None
    assert loaded["file_count"] == 2
