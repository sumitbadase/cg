"""Local git repository integration via GitPython."""

from git_integration.git_client import GitClient
from git_integration.inventory_builder import build_inventory_graph
from git_integration.inventory_store import InventoryStore
from git_integration.repo_scanner import RepoScanner, RepositoryInventory

__all__ = [
    "GitClient",
    "InventoryStore",
    "RepoScanner",
    "RepositoryInventory",
    "build_inventory_graph",
]
