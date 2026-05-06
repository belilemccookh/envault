"""Version history tracking for stored environment snapshots."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from envault.storage import _project_path

_HISTORY_FILE = "history.json"
_MAX_SNAPSHOTS = 20


def _history_path(project: str) -> Path:
    return _project_path(project) / _HISTORY_FILE


def _load_raw(project: str) -> list[dict[str, Any]]:
    path = _history_path(project)
    if not path.exists():
        return []
    with path.open() as fh:
        return json.load(fh)


def _save_raw(project: str, entries: list[dict[str, Any]]) -> None:
    path = _history_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(entries, fh, indent=2)


def record_snapshot(project: str, env: dict[str, str], note: str = "") -> None:
    """Append a snapshot of *env* to the project's history log."""
    entries = _load_raw(project)
    entries.append(
        {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "note": note,
            "env": dict(env),
        }
    )
    # Keep only the most recent snapshots
    entries = entries[-_MAX_SNAPSHOTS:]
    _save_raw(project, entries)


def list_snapshots(project: str) -> list[dict[str, Any]]:
    """Return all snapshots for *project*, oldest first."""
    return _load_raw(project)


def get_snapshot(project: str, index: int) -> dict[str, str]:
    """Return the env dict for snapshot at *index* (supports negative indexing).

    Raises IndexError if *index* is out of range.
    """
    entries = _load_raw(project)
    if not entries:
        raise IndexError(f"No history found for project '{project}'.")
    return entries[index]["env"]


def clear_history(project: str) -> int:
    """Delete all history for *project*. Returns number of entries removed."""
    entries = _load_raw(project)
    count = len(entries)
    path = _history_path(project)
    if path.exists():
        path.unlink()
    return count
