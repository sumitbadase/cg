"""Persist parsed repository inventories to local JSON storage."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from git_integration.repo_scanner import RepositoryInventory


class InventoryStore:
    """Store repository inventories and graph payloads on disk."""

    def __init__(self, storage_dir: str | Path) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        inventory: RepositoryInventory,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> Path:
        """Save inventory and graph payload under ``storage_dir/<repo_name>/``."""
        repo_dir = self.storage_dir / inventory.repository_name
        repo_dir.mkdir(parents=True, exist_ok=True)

        inventory_path = repo_dir / "inventory.json"
        graph_path = repo_dir / "graph_payload.json"

        payload = {
            "repository_name": inventory.repository_name,
            "local_path": inventory.local_path,
            "head_commit": inventory.head_commit,
            "active_branch": inventory.active_branch,
            "file_count": inventory.file_count,
            "directory_count": inventory.directory_count,
            "files": [asdict(file_record) for file_record in inventory.files],
            "directories": [asdict(directory_record) for directory_record in inventory.directories],
        }
        inventory_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        graph_path.write_text(
            json.dumps({"nodes": nodes, "edges": edges}, indent=2),
            encoding="utf-8",
        )
        return inventory_path

    def load(self, repository_name: str) -> dict[str, Any] | None:
        """Load a previously saved inventory, if present."""
        inventory_path = self.storage_dir / repository_name / "inventory.json"
        if not inventory_path.exists():
            return None
        return json.loads(inventory_path.read_text(encoding="utf-8"))
