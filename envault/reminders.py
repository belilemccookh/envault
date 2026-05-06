"""Reminders: schedule rotation reminders for projects."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from envault.storage import _base_dir


class ReminderError(Exception):
    pass


def _reminders_path() -> Path:
    path = _base_dir() / "reminders.json"
    return path


def _load() -> dict:
    p = _reminders_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _reminders_path().write_text(json.dumps(data, indent=2))


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def set_reminder(project: str, days: int, note: str = "") -> dict:
    """Schedule a rotation reminder *days* from now for *project*."""
    if days <= 0:
        raise ReminderError("days must be a positive integer")
    data = _load()
    due = (datetime.utcnow() + timedelta(days=days)).isoformat(timespec="seconds")
    entry = {"project": project, "due": due, "note": note, "created": _now_iso()}
    data[project] = entry
    _save(data)
    return entry


def get_reminder(project: str) -> Optional[dict]:
    """Return the reminder for *project*, or None."""
    return _load().get(project)


def delete_reminder(project: str) -> bool:
    """Remove the reminder for *project*. Returns True if it existed."""
    data = _load()
    if project not in data:
        return False
    del data[project]
    _save(data)
    return True


def list_reminders() -> list[dict]:
    """Return all reminders sorted by due date."""
    return sorted(_load().values(), key=lambda r: r["due"])


def due_reminders() -> list[dict]:
    """Return reminders whose due date is today or in the past."""
    now = _now_iso()
    return [r for r in list_reminders() if r["due"] <= now]
