"""Label management for envault projects.

Labels are free-form string tags attached to projects for categorisation,
distinct from structured tags (tags.py).  Each project can have zero or
more labels; duplicates are silently ignored.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envault.storage import _project_path  # reuse base storage dir helper


class LabelError(ValueError):
    """Raised when a label operation cannot be completed."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _labels_path(storage_dir: str) -> Path:
    return Path(storage_dir) / "_labels.json"


def _load(storage_dir: str) -> dict:
    p = _labels_path(storage_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(storage_dir: str, data: dict) -> None:
    _labels_path(storage_dir).write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def add_label(storage_dir: str, project: str, label: str) -> List[str]:
    """Attach *label* to *project*.  Returns updated label list."""
    if not project:
        raise LabelError("project name must not be empty")
    label = label.strip()
    if not label:
        raise LabelError("label must not be empty")
    data = _load(storage_dir)
    existing = data.get(project, [])
    if label not in existing:
        existing.append(label)
    data[project] = existing
    _save(storage_dir, data)
    return existing


def remove_label(storage_dir: str, project: str, label: str) -> List[str]:
    """Detach *label* from *project*.  Returns updated label list."""
    if not project:
        raise LabelError("project name must not be empty")
    data = _load(storage_dir)
    existing = data.get(project, [])
    existing = [l for l in existing if l != label]
    data[project] = existing
    _save(storage_dir, data)
    return existing


def get_labels(storage_dir: str, project: str) -> List[str]:
    """Return all labels attached to *project*."""
    return _load(storage_dir).get(project, [])


def find_by_label(storage_dir: str, label: str) -> List[str]:
    """Return projects that carry *label* (case-sensitive)."""
    return [proj for proj, labels in _load(storage_dir).items() if label in labels]


def clear_labels(storage_dir: str, project: str) -> None:
    """Remove every label from *project*."""
    data = _load(storage_dir)
    data.pop(project, None)
    _save(storage_dir, data)
