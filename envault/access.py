"""Access control: per-project read/write permission flags."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

ACCESS_FILENAME = "access.json"


class AccessError(Exception):
    """Raised for access-control violations or bad input."""


def _access_path(storage_dir: Path) -> Path:
    return storage_dir / ACCESS_FILENAME


def _load(storage_dir: Path) -> Dict[str, Dict[str, bool]]:
    path = _access_path(storage_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(storage_dir: Path, data: Dict[str, Dict[str, bool]]) -> None:
    _access_path(storage_dir).write_text(json.dumps(data, indent=2))


def set_permission(
    storage_dir: Path,
    project: str,
    *,
    can_read: bool = True,
    can_write: bool = True,
) -> Dict[str, bool]:
    """Set read/write permissions for *project*."""
    if not project:
        raise AccessError("Project name must not be empty.")
    data = _load(storage_dir)
    data[project] = {"read": can_read, "write": can_write}
    _save(storage_dir, data)
    return data[project]


def get_permission(storage_dir: Path, project: str) -> Dict[str, bool]:
    """Return the permission dict for *project* (defaults to full access)."""
    data = _load(storage_dir)
    return data.get(project, {"read": True, "write": True})


def check_read(storage_dir: Path, project: str) -> None:
    """Raise *AccessError* if *project* does not have read permission."""
    if not get_permission(storage_dir, project)["read"]:
        raise AccessError(f"Read access denied for project '{project}'.")


def check_write(storage_dir: Path, project: str) -> None:
    """Raise *AccessError* if *project* does not have write permission."""
    if not get_permission(storage_dir, project)["write"]:
        raise AccessError(f"Write access denied for project '{project}'.")


def list_permissions(storage_dir: Path) -> List[Dict[str, object]]:
    """Return a list of all explicit permission entries."""
    data = _load(storage_dir)
    return [
        {"project": project, **perms}
        for project, perms in sorted(data.items())
    ]


def remove_permission(storage_dir: Path, project: str) -> bool:
    """Remove explicit permissions for *project*. Returns True if removed."""
    data = _load(storage_dir)
    if project in data:
        del data[project]
        _save(storage_dir, data)
        return True
    return False
