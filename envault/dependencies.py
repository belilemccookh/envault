"""Track inter-project dependencies (project A requires project B's keys)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path.home() / ".envault"


class DependencyError(Exception):
    """Raised when a dependency operation fails."""


def _deps_path() -> Path:
    path = DATA_DIR / "dependencies.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _load() -> Dict[str, List[str]]:
    p = _deps_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, List[str]]) -> None:
    _deps_path().write_text(json.dumps(data, indent=2))


def add_dependency(project: str, depends_on: str) -> List[str]:
    """Record that *project* depends on *depends_on*."""
    if not project or not depends_on:
        raise DependencyError("Project name and dependency must be non-empty.")
    if project == depends_on:
        raise DependencyError("A project cannot depend on itself.")
    data = _load()
    deps = data.setdefault(project, [])
    if depends_on not in deps:
        deps.append(depends_on)
    _save(data)
    return deps


def remove_dependency(project: str, depends_on: str) -> List[str]:
    """Remove *depends_on* from *project*'s dependency list."""
    data = _load()
    deps = data.get(project, [])
    if depends_on not in deps:
        raise DependencyError(f"'{depends_on}' is not a dependency of '{project}'.")
    deps.remove(depends_on)
    data[project] = deps
    _save(data)
    return deps


def list_dependencies(project: str) -> List[str]:
    """Return all projects that *project* depends on."""
    return _load().get(project, [])


def list_dependents(project: str) -> List[str]:
    """Return all projects that depend on *project*."""
    return [p for p, deps in _load().items() if project in deps]


def all_dependencies() -> Dict[str, List[str]]:
    """Return the full dependency map."""
    return _load()
