"""Retention policy management for envault projects."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.storage import _project_path  # noqa: F401 – reuse base dir logic


class RetentionError(Exception):
    """Raised when a retention operation fails."""


_DEFAULT_MAX_SNAPSHOTS = 10
_DEFAULT_MAX_HISTORY = 50


def _retention_path(storage_dir: Path) -> Path:
    return storage_dir / "_retention.json"


def _load(storage_dir: Path) -> dict:
    path = _retention_path(storage_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(storage_dir: Path, data: dict) -> None:
    _retention_path(storage_dir).write_text(json.dumps(data, indent=2))


def set_policy(
    project: str,
    storage_dir: Path,
    *,
    max_snapshots: Optional[int] = None,
    max_history: Optional[int] = None,
) -> dict:
    """Set retention limits for a project.  Returns the stored policy."""
    if not project:
        raise RetentionError("Project name must not be empty.")
    if max_snapshots is not None and max_snapshots < 1:
        raise RetentionError("max_snapshots must be at least 1.")
    if max_history is not None and max_history < 1:
        raise RetentionError("max_history must be at least 1.")

    data = _load(storage_dir)
    policy = data.get(project, {})
    if max_snapshots is not None:
        policy["max_snapshots"] = max_snapshots
    if max_history is not None:
        policy["max_history"] = max_history
    data[project] = policy
    _save(storage_dir, data)
    return dict(policy)


def get_policy(project: str, storage_dir: Path) -> dict:
    """Return the retention policy for *project*, falling back to defaults."""
    if not project:
        raise RetentionError("Project name must not be empty.")
    data = _load(storage_dir)
    policy = data.get(project, {})
    return {
        "max_snapshots": policy.get("max_snapshots", _DEFAULT_MAX_SNAPSHOTS),
        "max_history": policy.get("max_history", _DEFAULT_MAX_HISTORY),
    }


def delete_policy(project: str, storage_dir: Path) -> bool:
    """Remove the retention policy for *project*.  Returns True if it existed."""
    data = _load(storage_dir)
    if project not in data:
        return False
    del data[project]
    _save(storage_dir, data)
    return True


def list_policies(storage_dir: Path) -> dict:
    """Return all stored retention policies keyed by project name."""
    return dict(_load(storage_dir))
