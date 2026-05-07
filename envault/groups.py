"""Project grouping — organise projects into named groups."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envault.storage import _base_dir


class GroupError(Exception):
    """Raised for invalid group operations."""


def _groups_path() -> Path:
    path = _base_dir() / "groups.json"
    return path


def _load() -> Dict[str, List[str]]:
    p = _groups_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, List[str]]) -> None:
    _groups_path().write_text(json.dumps(data, indent=2))


def add_project(group: str, project: str) -> List[str]:
    """Add *project* to *group*, creating the group if needed."""
    if not group:
        raise GroupError("Group name must not be empty.")
    if not project:
        raise GroupError("Project name must not be empty.")
    data = _load()
    members = data.setdefault(group, [])
    if project not in members:
        members.append(project)
    _save(data)
    return list(members)


def remove_project(group: str, project: str) -> List[str]:
    """Remove *project* from *group*."""
    data = _load()
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    members = data[group]
    if project not in members:
        raise GroupError(f"Project '{project}' is not in group '{group}'.")
    members.remove(project)
    if not members:
        del data[group]
    _save(data)
    return list(members)


def list_groups() -> Dict[str, List[str]]:
    """Return all groups and their members."""
    return _load()


def get_group(group: str) -> List[str]:
    """Return members of *group*, raising GroupError if absent."""
    data = _load()
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    return list(data[group])


def delete_group(group: str) -> None:
    """Delete an entire group."""
    data = _load()
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    del data[group]
    _save(data)
