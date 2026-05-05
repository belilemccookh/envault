"""Diff utilities for comparing .env snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    @property
    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        if not parts:
            return "No changes."
        return ", ".join(parts)


def diff_envs(old: Dict[str, str], new: Dict[str, str]) -> DiffResult:
    """Compare two env dicts and return a DiffResult."""
    result = DiffResult()
    all_keys = set(old) | set(new)
    for key in all_keys:
        if key in old and key not in new:
            result.removed[key] = old[key]
        elif key not in old and key in new:
            result.added[key] = new[key]
        elif old[key] != new[key]:
            result.changed[key] = (old[key], new[key])
        else:
            result.unchanged[key] = old[key]
    return result


def format_diff(result: DiffResult, mask_values: bool = True) -> List[str]:
    """Return a list of coloured-style diff lines (plain text)."""
    lines: List[str] = []

    def _val(v: str) -> str:
        return "***" if mask_values else v

    for k, v in sorted(result.added.items()):
        lines.append(f"+ {k}={_val(v)}")
    for k, v in sorted(result.removed.items()):
        lines.append(f"- {k}={_val(v)}")
    for k, (old_v, new_v) in sorted(result.changed.items()):
        lines.append(f"~ {k}: {_val(old_v)} -> {_val(new_v)}")
    return lines
