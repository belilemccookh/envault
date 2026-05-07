"""Expiry management for stored environment projects."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from envault.storage import _project_path, BASE_DIR


class ExpiryError(ValueError):
    """Raised when expiry operations fail."""


def _expiry_path(base_dir: Path = BASE_DIR) -> Path:
    return base_dir / "expiry.json"


def _load(base_dir: Path = BASE_DIR) -> dict:
    path = _expiry_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(data: dict, base_dir: Path = BASE_DIR) -> None:
    _expiry_path(base_dir).write_text(json.dumps(data, indent=2))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def set_expiry(project: str, days: int, base_dir: Path = BASE_DIR) -> dict:
    """Set an expiry date *days* from now for *project*."""
    if not project:
        raise ExpiryError("Project name must not be empty.")
    if days <= 0:
        raise ExpiryError("days must be a positive integer.")
    expires_at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    data = _load(base_dir)
    data[project] = {"expires_at": expires_at, "set_at": _now_iso()}
    _save(data, base_dir)
    return data[project]


def get_expiry(project: str, base_dir: Path = BASE_DIR) -> Optional[dict]:
    """Return expiry info for *project*, or None if not set."""
    return _load(base_dir).get(project)


def remove_expiry(project: str, base_dir: Path = BASE_DIR) -> bool:
    """Remove expiry for *project*. Returns True if it existed."""
    data = _load(base_dir)
    if project not in data:
        return False
    del data[project]
    _save(data, base_dir)
    return True


def is_expired(project: str, base_dir: Path = BASE_DIR) -> bool:
    """Return True if *project* has an expiry date that has passed."""
    entry = get_expiry(project, base_dir)
    if entry is None:
        return False
    expires_at = datetime.fromisoformat(entry["expires_at"])
    return datetime.now(timezone.utc) >= expires_at


def list_expiries(base_dir: Path = BASE_DIR) -> dict:
    """Return all expiry entries keyed by project name."""
    return _load(base_dir)
