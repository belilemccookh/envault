"""Scheduled / named snapshots for envault projects."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from envault.storage import _project_path


class SnapshotError(Exception):
    """Raised for snapshot-related failures."""


def _snapshots_path(project: str) -> Path:
    return _project_path(project) / "snapshots.json"


def _load(project: str) -> list[dict[str, Any]]:
    p = _snapshots_path(project)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save(project: str, data: list[dict[str, Any]]) -> None:
    p = _snapshots_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_snapshot(project: str, label: str, env: dict[str, str]) -> dict[str, Any]:
    """Persist a named snapshot for *project* with the given *env* dict."""
    if not label or not label.strip():
        raise SnapshotError("Snapshot label must not be empty.")
    data = _load(project)
    entry: dict[str, Any] = {
        "id": len(data) + 1,
        "label": label.strip(),
        "created_at": _now_iso(),
        "env": env,
    }
    data.append(entry)
    _save(project, data)
    return entry


def list_snapshots(project: str) -> list[dict[str, Any]]:
    """Return all snapshots for *project* (oldest first)."""
    return _load(project)


def get_snapshot(project: str, snapshot_id: int) -> dict[str, Any]:
    """Return a single snapshot by numeric *id* or raise SnapshotError."""
    for entry in _load(project):
        if entry["id"] == snapshot_id:
            return entry
    raise SnapshotError(f"Snapshot #{snapshot_id} not found for project '{project}'.")


def delete_snapshot(project: str, snapshot_id: int) -> None:
    """Remove snapshot *snapshot_id* from *project*."""
    data = _load(project)
    filtered = [e for e in data if e["id"] != snapshot_id]
    if len(filtered) == len(data):
        raise SnapshotError(f"Snapshot #{snapshot_id} not found for project '{project}'.")
    _save(project, filtered)
