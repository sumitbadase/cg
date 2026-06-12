"""Scan a local git working tree and build a repository inventory."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from exceptions import GitRepositoryError, ParserError
from git_integration.git_client import GitClient

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".idea",
    ".pytest_cache",
}


@dataclass
class FileRecord:
    """Metadata for a single file in the repository."""

    path: str
    extension: str
    size_bytes: int


@dataclass
class DirectoryRecord:
    """Metadata for a directory in the repository."""

    path: str
    file_count: int


@dataclass
class RepositoryInventory:
    """Parsed inventory for a local git repository."""

    repository_name: str
    local_path: str
    head_commit: str
    active_branch: str
    files: list[FileRecord] = field(default_factory=list)
    directories: list[DirectoryRecord] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def directory_count(self) -> int:
        return len(self.directories)


class RepoScanner:
    """Walk a repository working tree and collect file inventory."""

    def __init__(self, git_client: GitClient | None = None) -> None:
        self.git_client = git_client or GitClient(base_dir=".")

    def scan(
        self,
        repo_path: str | Path,
        *,
        max_files: int | None = None,
    ) -> RepositoryInventory:
        """Scan repository files under the current HEAD working tree.

        Args:
            repo_path: Path to local repository root.
            max_files: Optional cap for very large repositories.

        Returns:
            Repository inventory with files and directories.
        """
        path = Path(repo_path).resolve()
        if not path.is_dir():
            raise GitRepositoryError(f"Repository path does not exist: {path}")

        metadata = self.git_client.metadata(path)
        repo_name = path.name
        files: list[FileRecord] = []
        dir_file_counts: dict[str, int] = {}

        logger.info("Scanning repository {} at {}", repo_name, path)
        for file_path in path.rglob("*"):
            if not file_path.is_file():
                continue
            if _should_skip(file_path, path):
                continue

            relative = file_path.relative_to(path).as_posix()
            parent = file_path.parent.relative_to(path).as_posix()
            if parent == ".":
                parent = ""
            dir_file_counts[parent] = dir_file_counts.get(parent, 0) + 1

            files.append(
                FileRecord(
                    path=relative,
                    extension=file_path.suffix.lower(),
                    size_bytes=file_path.stat().st_size,
                )
            )
            if max_files is not None and len(files) >= max_files:
                logger.warning("Reached max_files={} while scanning {}", max_files, repo_name)
                break

        if not files and max_files != 0:
            raise ParserError(f"No scannable files found in repository: {path}")

        directories = [
            DirectoryRecord(path=directory or ".", file_count=count)
            for directory, count in sorted(dir_file_counts.items())
        ]

        return RepositoryInventory(
            repository_name=repo_name,
            local_path=str(path),
            head_commit=metadata["head_commit"],
            active_branch=metadata["active_branch"],
            files=files,
            directories=directories,
        )


def _should_skip(file_path: Path, repo_root: Path) -> bool:
    relative_parts = file_path.relative_to(repo_root).parts
    return any(part in SKIP_DIR_NAMES for part in relative_parts)
