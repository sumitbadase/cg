"""Clone or update GitHub repositories for local analysis."""

from __future__ import annotations

from pathlib import Path

from git_integration.git_client import GitClient
from utils import get_repo_storage_dir


def pull_repositories(repos: list[str], target_dir: str | Path | None = None) -> list[Path]:
    """Clone or pull a list of GitHub repositories into a target directory.

    Args:
        repos: List of repository URLs or ``owner/name`` slugs.
        target_dir: Optional override for repository storage root.

    Returns:
        List of paths to cloned repository directories.
    """
    base_dir = Path(target_dir) if target_dir is not None else get_repo_storage_dir()
    client = GitClient(base_dir=base_dir)
    cloned: list[Path] = []

    for repo in repos:
        cloned.append(client.clone_or_pull(repo))

    return cloned
