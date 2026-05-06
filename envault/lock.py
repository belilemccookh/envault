"""Project locking — prevent concurrent writes to the same project."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional

from envault.storage import _project_path

_LOCK_SUFFIX = ".lock"
_STALE_AFTER = 30  # seconds


class LockError(RuntimeError):
    """Raised when a project lock cannot be acquired."""


def _lock_path(project: str) -> Path:
    return _project_path(project).with_suffix(_LOCK_SUFFIX)


def acquire(project: str, timeout: float = 5.0, poll: float = 0.1) -> None:
    """Acquire an exclusive lock for *project*.

    Raises LockError if the lock cannot be obtained within *timeout* seconds.
    Stale locks older than _STALE_AFTER seconds are removed automatically.
    """
    lock = _lock_path(project)
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout

    while True:
        _clear_stale(lock)
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return
        except FileExistsError:
            if time.monotonic() >= deadline:
                owner = _lock_owner(lock)
                raise LockError(
                    f"Project '{project}' is locked by PID {owner}. "
                    "Try again shortly."
                )
            time.sleep(poll)


def release(project: str) -> None:
    """Release the lock for *project* (no-op if not locked)."""
    lock = _lock_path(project)
    try:
        lock.unlink()
    except FileNotFoundError:
        pass


def is_locked(project: str) -> bool:
    """Return True if *project* currently holds a lock."""
    lock = _lock_path(project)
    _clear_stale(lock)
    return lock.exists()


def _clear_stale(lock: Path) -> None:
    try:
        age = time.time() - lock.stat().st_mtime
        if age > _STALE_AFTER:
            lock.unlink(missing_ok=True)
    except FileNotFoundError:
        pass


def _lock_owner(lock: Path) -> Optional[str]:
    try:
        return lock.read_text().strip()
    except OSError:
        return "unknown"
