"""Favorites — mark frequently-used projects for quick access."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envault import storage


class FavoriteError(Exception):
    """Raised for invalid favorite operations."""


def _favorites_path() -> Path:
    base = storage._project_path("__meta__").parent
    return base / "favorites.json"


def _load() -> List[str]:
    p = _favorites_path()
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save(favorites: List[str]) -> None:
    p = _favorites_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(favorites, indent=2))


def add_favorite(project: str) -> None:
    """Mark *project* as a favorite (idempotent)."""
    if not project or not project.strip():
        raise FavoriteError("Project name must not be empty.")
    project = project.strip()
    favs = _load()
    if project not in favs:
        favs.append(project)
        _save(favs)


def remove_favorite(project: str) -> None:
    """Remove *project* from favorites; raises if not present."""
    favs = _load()
    if project not in favs:
        raise FavoriteError(f"Project '{project}' is not in favorites.")
    favs.remove(project)
    _save(favs)


def list_favorites() -> List[str]:
    """Return all favorited project names in insertion order."""
    return list(_load())


def is_favorite(project: str) -> bool:
    """Return True if *project* is currently favorited."""
    return project in _load()


def clear_favorites() -> int:
    """Remove all favorites and return how many were cleared."""
    favs = _load()
    count = len(favs)
    _save([])
    return count
