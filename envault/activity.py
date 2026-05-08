"""Track per-project activity statistics (reads, writes, deletes)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from envault.storage import _base_path


class ActivityError(Exception):
    pass


def _activity_path() -> Path:
    p = _base_path() / "activity.json"
    return p


def _load() -> dict[str, Any]:
    p = _activity_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict[str, Any]) -> None:
    _activity_path().write_text(json.dumps(data, indent=2))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_activity(project: str, action: str) -> dict[str, Any]:
    """Increment the counter for *action* on *project* and update last_seen."""
    if not project:
        raise ActivityError("project name must not be empty")
    valid = {"read", "write", "delete"}
    if action not in valid:
        raise ActivityError(f"action must be one of {valid}")

    data = _load()
    entry = data.setdefault(
        project,
        {"read": 0, "write": 0, "delete": 0, "last_seen": None},
    )
    entry[action] += 1
    entry["last_seen"] = _now_iso()
    _save(data)
    return dict(entry)


def get_activity(project: str) -> dict[str, Any]:
    """Return activity counters for *project*, or zeroed entry if absent."""
    if not project:
        raise ActivityError("project name must not be empty")
    data = _load()
    return data.get(project, {"read": 0, "write": 0, "delete": 0, "last_seen": None})


def all_activity() -> dict[str, Any]:
    """Return the full activity log."""
    return _load()


def reset_activity(project: str) -> None:
    """Remove activity record for *project*."""
    if not project:
        raise ActivityError("project name must not be empty")
    data = _load()
    data.pop(project, None)
    _save(data)
