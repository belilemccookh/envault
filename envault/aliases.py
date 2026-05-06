"""Project alias management — short names that map to full project identifiers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envault.storage import _base_dir


class AliasError(Exception):
    """Raised for invalid alias operations."""


def _aliases_path() -> Path:
    path = _base_dir() / "aliases.json"
    return path


def _load() -> Dict[str, str]:
    p = _aliases_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, str]) -> None:
    _aliases_path().write_text(json.dumps(data, indent=2, sort_keys=True))


def set_alias(alias: str, project: str) -> None:
    """Map *alias* to *project*. Overwrites any existing mapping."""
    alias = alias.strip()
    project = project.strip()
    if not alias:
        raise AliasError("Alias must not be empty.")
    if not project:
        raise AliasError("Project name must not be empty.")
    if "/" in alias or "\\" in alias:
        raise AliasError("Alias must not contain path separators.")
    data = _load()
    data[alias] = project
    _save(data)


def remove_alias(alias: str) -> None:
    """Remove *alias*. Raises AliasError if it does not exist."""
    data = _load()
    if alias not in data:
        raise AliasError(f"Alias '{alias}' not found.")
    del data[alias]
    _save(data)


def resolve(alias: str) -> Optional[str]:
    """Return the project name for *alias*, or None if not found."""
    return _load().get(alias)


def resolve_or_name(name: str) -> str:
    """Return the project mapped to *name* if it is an alias, else *name* itself."""
    return resolve(name) or name


def list_aliases() -> Dict[str, str]:
    """Return a copy of all alias → project mappings."""
    return dict(_load())


def clear_aliases() -> None:
    """Remove every alias (used in tests / reset scenarios)."""
    _save({})
