"""Per-project key quota management for envault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

QUOTA_FILENAME = "quotas.json"
DEFAULT_MAX_KEYS = 100


class QuotaError(Exception):
    """Raised when a quota operation fails."""


def _quota_path(storage_dir: Path) -> Path:
    return storage_dir / QUOTA_FILENAME


def _load(storage_dir: Path) -> dict:
    path = _quota_path(storage_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(storage_dir: Path, data: dict) -> None:
    _quota_path(storage_dir).write_text(json.dumps(data, indent=2))


def set_quota(storage_dir: Path, project: str, max_keys: int) -> dict:
    """Set the maximum number of keys allowed for a project."""
    if not project:
        raise QuotaError("Project name must not be empty.")
    if max_keys < 1:
        raise QuotaError("max_keys must be at least 1.")
    data = _load(storage_dir)
    data[project] = {"max_keys": max_keys}
    _save(storage_dir, data)
    return data[project]


def get_quota(storage_dir: Path, project: str) -> int:
    """Return the max keys for a project, or the default if not set."""
    if not project:
        raise QuotaError("Project name must not be empty.")
    data = _load(storage_dir)
    return data.get(project, {}).get("max_keys", DEFAULT_MAX_KEYS)


def remove_quota(storage_dir: Path, project: str) -> bool:
    """Remove a project's quota entry. Returns True if it existed."""
    if not project:
        raise QuotaError("Project name must not be empty.")
    data = _load(storage_dir)
    if project not in data:
        return False
    del data[project]
    _save(storage_dir, data)
    return True


def check_quota(storage_dir: Path, project: str, current_key_count: int) -> None:
    """Raise QuotaError if current_key_count meets or exceeds the project quota."""
    limit = get_quota(storage_dir, project)
    if current_key_count >= limit:
        raise QuotaError(
            f"Project '{project}' has reached its key quota ({limit} keys). "
            "Remove keys or increase the quota before adding more."
        )


def list_quotas(storage_dir: Path) -> dict[str, int]:
    """Return a mapping of project -> max_keys for all projects with explicit quotas."""
    data = _load(storage_dir)
    return {project: entry["max_keys"] for project, entry in data.items()}
