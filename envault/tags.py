"""Tag management for envault projects.

Allows users to assign and query tags (e.g. 'production', 'staging') on
stored projects so they can be grouped and filtered.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envault.storage import _base_dir

_TAGS_FILE = "tags.json"


def _tags_path() -> Path:
    path = _base_dir() / _TAGS_FILE
    return path


def _load() -> Dict[str, List[str]]:
    """Return the full tag mapping {project: [tag, ...]}."""
    p = _tags_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, List[str]]) -> None:
    _tags_path().write_text(json.dumps(data, indent=2, sort_keys=True))


def add_tag(project: str, tag: str) -> None:
    """Add *tag* to *project*. No-op if already present."""
    data = _load()
    tags = data.setdefault(project, [])
    tag = tag.strip().lower()
    if tag not in tags:
        tags.append(tag)
        tags.sort()
        _save(data)


def remove_tag(project: str, tag: str) -> bool:
    """Remove *tag* from *project*. Returns True if it existed."""
    data = _load()
    tags = data.get(project, [])
    tag = tag.strip().lower()
    if tag in tags:
        tags.remove(tag)
        if not tags:
            data.pop(project, None)
        _save(data)
        return True
    return False


def get_tags(project: str) -> List[str]:
    """Return sorted list of tags for *project*."""
    return sorted(_load().get(project, []))


def projects_with_tag(tag: str) -> List[str]:
    """Return sorted list of projects that carry *tag*."""
    tag = tag.strip().lower()
    return sorted(p for p, tags in _load().items() if tag in tags)


def all_tags() -> Dict[str, List[str]]:
    """Return the complete {project: [tags]} mapping."""
    return _load()


def clear_tags(project: str) -> None:
    """Remove all tags for *project*."""
    data = _load()
    data.pop(project, None)
    _save(data)
