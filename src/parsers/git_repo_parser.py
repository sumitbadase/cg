"""Parse local git repositories into normalized inventory records."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from git_integration.git_client import GitClient
from git_integration.inventory_builder import build_inventory_graph
from git_integration.inventory_store import InventoryStore
from git_integration.repo_scanner import RepoScanner
from utils import get_inventory_storage_dir, get_repo_storage_dir


def parse_and_store_repository(
    repo_path: str | Path,
    *,
    max_files: int | None = None,
    store_inventory: bool = True,
) -> dict[str, Any]:
    """Scan a local git repository and optionally persist inventory/graph payload.

    Args:
        repo_path: Path to a cloned repository root.
        max_files: Optional scan cap for very large repositories.
        store_inventory: Whether to write JSON artifacts to disk.

    Returns:
        Summary dictionary with counts and storage paths.
    """
    scanner = RepoScanner(git_client=GitClient(base_dir=get_repo_storage_dir()))
    inventory = scanner.scan(repo_path, max_files=max_files)
    nodes, edges = build_inventory_graph(inventory)

    inventory_path: str | None = None
    if store_inventory:
        store = InventoryStore(get_inventory_storage_dir())
        saved_path = store.save(inventory, nodes, edges)
        inventory_path = str(saved_path)

    return {
        "repository_name": inventory.repository_name,
        "local_path": inventory.local_path,
        "head_commit": inventory.head_commit,
        "active_branch": inventory.active_branch,
        "file_count": inventory.file_count,
        "directory_count": inventory.directory_count,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "inventory_path": inventory_path,
    }
