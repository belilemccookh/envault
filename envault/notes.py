"""Per-project plaintext notes stored alongside encrypted env data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envault.storage import _project_path


def _notes_path(project: str) -> Path:
    return _project_path(project) / "notes.json"


def _load(project: str) -> List[dict]:
    path = _notes_path(project)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _save(project: str, entries: List[dict]) -> None:
    path = _notes_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def add_note(project: str, text: str) -> dict:
    """Append a note to *project* and return the new entry."""
    if not text or not text.strip():
        raise ValueError("Note text must not be empty.")
    entries = _load(project)
    entry = {"id": len(entries) + 1, "ts": _now_iso(), "text": text.strip()}
    entries.append(entry)
    _save(project, entries)
    return entry


def list_notes(project: str) -> List[dict]:
    """Return all notes for *project* in insertion order."""
    return _load(project)


def delete_note(project: str, note_id: int) -> bool:
    """Delete note by *note_id*. Returns True if found and removed."""
    entries = _load(project)
    new_entries = [e for e in entries if e["id"] != note_id]
    if len(new_entries) == len(entries):
        return False
    _save(project, new_entries)
    return True


def clear_notes(project: str) -> int:
    """Remove all notes for *project*. Returns number of notes deleted."""
    entries = _load(project)
    _save(project, [])
    return len(entries)


def get_note(project: str, note_id: int) -> Optional[dict]:
    """Return a single note by id, or None if not found."""
    for entry in _load(project):
        if entry["id"] == note_id:
            return entry
    return None
