"""Pin management — mark specific env var keys as protected across projects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envault.storage import _base_dir


class PinError(Exception):
    """Raised when a pin operation fails."""


def _pins_path() -> Path:
    path = _base_dir() / "pins.json"
    return path


def _load() -> Dict[str, List[str]]:
    """Return mapping of project -> list of pinned keys."""
    p = _pins_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, List[str]]) -> None:
    _pins_path().write_text(json.dumps(data, indent=2))


def pin_key(project: str, key: str) -> None:
    """Pin *key* for *project* so it is flagged as protected."""
    if not project:
        raise PinError("project name must not be empty")
    if not key:
        raise PinError("key name must not be empty")
    data = _load()
    pins = data.setdefault(project, [])
    if key not in pins:
        pins.append(key)
    _save(data)


def unpin_key(project: str, key: str) -> bool:
    """Remove pin for *key* in *project*. Returns True if it existed."""
    data = _load()
    pins = data.get(project, [])
    if key not in pins:
        return False
    pins.remove(key)
    if not pins:
        del data[project]
    _save(data)
    return True


def get_pins(project: str) -> List[str]:
    """Return all pinned keys for *project*."""
    return list(_load().get(project, []))


def is_pinned(project: str, key: str) -> bool:
    """Return True if *key* is pinned for *project*."""
    return key in _load().get(project, [])


def all_pins() -> Dict[str, List[str]]:
    """Return the full pins mapping."""
    return _load()
