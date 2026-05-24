"""Clone or update GitHub repositories for local analysis."""

from __future__ import annotations

import subprocess
from pathlib import Path


def pull_repositories(repos: list[str], target_dir: str | Path) -> list[Path]:
    """Clone or pull a list of GitHub repositories into a target directory.

    Args:
        repos: List of repository URLs or ``owner/name`` slugs.
        target_dir: Local directory to store cloned repositories.

    Returns:
        List of paths to cloned repository directories.
    """
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    cloned: list[Path] = []

    for repo in repos:
        # TODO: Resolve slug to clone URL, skip if already cloned, git pull otherwise
        repo_name = repo.rstrip("/").split("/")[-1].removesuffix(".git")
        dest = target / repo_name
        cloned.append(dest)

        if dest.exists():
            subprocess.run(["git", "-C", str(dest), "pull"], check=False)  # noqa: S603
        else:
            clone_url = repo if repo.startswith("http") else f"https://github.com/{repo}.git"
            subprocess.run(["git", "clone", clone_url, str(dest)], check=False)  # noqa: S603

    return cloned
