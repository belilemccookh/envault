"""Audit log for tracking envault operations (set, get, delete, rotate, export)."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

APP_DIR = Path(os.environ.get("ENVAULT_HOME", Path.home() / ".envault"))
AUDIT_LOG_PATH = APP_DIR / "audit.log"

MAX_ENTRIES = 1000  # Rolling cap to prevent unbounded growth


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def record(
    action: str,
    project: str,
    detail: Optional[str] = None,
    success: bool = True,
) -> None:
    """Append a single audit entry to the log file."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": _now_iso(),
        "action": action,
        "project": project,
        "detail": detail,
        "success": success,
    }
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    _trim_log()


def _trim_log() -> None:
    """Keep only the most recent MAX_ENTRIES lines."""
    if not AUDIT_LOG_PATH.exists():
        return
    lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    if len(lines) > MAX_ENTRIES:
        AUDIT_LOG_PATH.write_text("".join(lines[-MAX_ENTRIES:]), encoding="utf-8")


def read_log(project: Optional[str] = None, limit: int = 50) -> list[dict]:
    """Return the most recent *limit* audit entries, optionally filtered by project."""
    if not AUDIT_LOG_PATH.exists():
        return []
    lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    entries = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if project is None or entry.get("project") == project:
            entries.append(entry)
        if len(entries) >= limit:
            break
    return entries


def clear_log() -> None:
    """Erase the audit log entirely (used in tests / explicit user request)."""
    if AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.unlink()
