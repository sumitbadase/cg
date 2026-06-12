"""Build graph-ready node and edge payloads from repository inventory."""

from __future__ import annotations

from typing import Any

from git_integration.repo_scanner import RepositoryInventory


def build_inventory_graph(inventory: RepositoryInventory) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Convert a repository inventory into graph nodes and edges.

    Nodes:
        - Repository
        - Directory
        - File

    Edges:
        - CONTAINS (repository -> directory/file, directory -> file)
    """
    repo_id = f"repo:{inventory.repository_name}"
    nodes: list[dict[str, Any]] = [
        {
            "id": repo_id,
            "label": "Repository",
            "name": inventory.repository_name,
            "path": inventory.local_path,
            "head_commit": inventory.head_commit,
            "active_branch": inventory.active_branch,
        }
    ]
    edges: list[dict[str, Any]] = []
    seen_dirs: set[str] = set()

    for directory in inventory.directories:
        dir_id = _directory_id(inventory.repository_name, directory.path)
        if dir_id not in seen_dirs:
            nodes.append(
                {
                    "id": dir_id,
                    "label": "Directory",
                    "path": directory.path,
                    "file_count": directory.file_count,
                }
            )
            seen_dirs.add(dir_id)
            parent_id = _parent_directory_id(inventory.repository_name, directory.path)
            edges.append(
                {
                    "from": parent_id,
                    "to": dir_id,
                    "label": "CONTAINS",
                }
            )

    for file_record in inventory.files:
        file_id = f"file:{inventory.repository_name}:{file_record.path}"
        parent_path = _parent_path(file_record.path)
        parent_id = (
            _directory_id(inventory.repository_name, parent_path)
            if parent_path
            else repo_id
        )
        nodes.append(
            {
                "id": file_id,
                "label": "File",
                "path": file_record.path,
                "extension": file_record.extension,
                "size_bytes": file_record.size_bytes,
            }
        )
        edges.append({"from": parent_id, "to": file_id, "label": "CONTAINS"})

    return nodes, edges


def _parent_path(file_path: str) -> str:
    if "/" not in file_path:
        return ""
    return file_path.rsplit("/", 1)[0]


def _directory_id(repository_name: str, directory_path: str) -> str:
    normalized = directory_path or "."
    return f"dir:{repository_name}:{normalized}"


def _parent_directory_id(repository_name: str, directory_path: str) -> str:
    if not directory_path or directory_path == ".":
        return f"repo:{repository_name}"
    parent = _parent_path(directory_path)
    return _directory_id(repository_name, parent) if parent else f"repo:{repository_name}"
