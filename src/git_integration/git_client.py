"""GitPython wrapper for cloning and managing local repositories."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from loguru import logger

from exceptions import GitRepositoryError


def resolve_clone_url(repository: str) -> str:
    """Convert a slug or URL into a clone URL."""
    value = repository.strip().rstrip("/")
    if value.startswith("http://") or value.startswith("https://") or value.startswith("git@"):
        return value if value.endswith(".git") else f"{value}.git"
    return f"https://github.com/{value}.git"


def repo_name_from_url(url: str) -> str:
    """Extract repository directory name from a clone URL."""
    path = urlparse(url).path.rstrip("/")
    return path.split("/")[-1].removesuffix(".git")


class GitClient:
    """Clone, open, and sync git repositories on disk."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def clone_or_pull(
        self,
        repository: str,
        *,
        target_directory: str | Path | None = None,
        depth: int | None = None,
    ) -> Path:
        """Clone a repository or pull latest changes if it already exists.

        Args:
            repository: Clone URL or ``owner/name`` slug.
            target_directory: Optional destination folder name or absolute path.
            depth: Optional shallow clone depth.

        Returns:
            Path to the local repository root.
        """
        clone_url = resolve_clone_url(repository)
        dest = self._resolve_destination(clone_url, target_directory)

        if dest.exists() and (dest / ".git").is_dir():
            logger.info("Pulling existing repository at {}", dest)
            try:
                repo = Repo(dest)
                repo.remotes.origin.pull()
            except (GitCommandError, InvalidGitRepositoryError) as exc:
                raise GitRepositoryError(
                    f"Failed to pull repository at {dest}",
                    details={"error": str(exc)},
                ) from exc
            return dest

        logger.info("Cloning {} into {}", clone_url, dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        clone_kwargs: dict[str, Any] = {}
        if depth is not None:
            clone_kwargs["depth"] = depth

        try:
            Repo.clone_from(clone_url, dest, **clone_kwargs)
        except GitCommandError as exc:
            raise GitRepositoryError(
                f"Failed to clone repository {clone_url}",
                details={"error": str(exc), "destination": str(dest)},
            ) from exc

        return dest

    def open(self, repo_path: str | Path) -> Repo:
        """Open an existing local git repository."""
        path = Path(repo_path)
        try:
            return Repo(path)
        except InvalidGitRepositoryError as exc:
            raise GitRepositoryError(
                f"Not a valid git repository: {path}",
                details={"path": str(path)},
            ) from exc

    def metadata(self, repo_path: str | Path) -> dict[str, Any]:
        """Return basic metadata for a local repository."""
        repo = self.open(repo_path)
        head = repo.head.commit
        return {
            "path": str(Path(repo_path).resolve()),
            "active_branch": repo.active_branch.name,
            "head_commit": head.hexsha,
            "head_message": head.message.strip(),
            "head_author": str(head.author),
            "head_committed_at": head.committed_datetime.isoformat(),
            "branch_count": len(list(repo.branches)),
            "remote_urls": [remote.url for remote in repo.remotes],
        }

    def _resolve_destination(
        self,
        clone_url: str,
        target_directory: str | Path | None,
    ) -> Path:
        if target_directory is None:
            return self.base_dir / repo_name_from_url(clone_url)

        target = Path(target_directory)
        if target.is_absolute():
            return target
        return self.base_dir / target
