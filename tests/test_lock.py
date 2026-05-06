"""Tests for envault.lock."""

from __future__ import annotations

import os
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from envault import lock as locklib
from envault.lock import LockError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    """Redirect storage root to a temp directory."""
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    import envault.storage as st
    monkeypatch.setattr(st, "_BASE", tmp_path)
    import envault.lock as lk
    monkeypatch.setattr(lk, "_project_path", st._project_path)
    yield tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAcquireRelease:
    def test_acquire_creates_lock_file(self):
        locklib.acquire("alpha")
        assert locklib._lock_path("alpha").exists()
        locklib.release("alpha")

    def test_lock_file_contains_pid(self):
        locklib.acquire("beta")
        owner = locklib._lock_path("beta").read_text().strip()
        assert owner == str(os.getpid())
        locklib.release("beta")

    def test_release_removes_file(self):
        locklib.acquire("gamma")
        locklib.release("gamma")
        assert not locklib._lock_path("gamma").exists()

    def test_release_noop_when_not_locked(self):
        locklib.release("nonexistent")  # should not raise

    def test_is_locked_true_after_acquire(self):
        locklib.acquire("delta")
        assert locklib.is_locked("delta")
        locklib.release("delta")

    def test_is_locked_false_after_release(self):
        locklib.acquire("epsilon")
        locklib.release("epsilon")
        assert not locklib.is_locked("epsilon")

    def test_double_acquire_raises_lock_error(self):
        locklib.acquire("zeta")
        try:
            with pytest.raises(LockError, match="zeta"):
                locklib.acquire("zeta", timeout=0.2, poll=0.05)
        finally:
            locklib.release("zeta")

    def test_stale_lock_is_cleared(self, tmp_storage):
        locklib.acquire("eta")
        lock_file = locklib._lock_path("eta")
        # Back-date the lock file to simulate a stale lock
        old_time = time.time() - locklib._STALE_AFTER - 5
        os.utime(str(lock_file), (old_time, old_time))
        # Should succeed because stale lock is cleared
        locklib.acquire("eta")
        locklib.release("eta")

    def test_is_locked_false_for_stale_lock(self, tmp_storage):
        locklib.acquire("theta")
        lock_file = locklib._lock_path("theta")
        old_time = time.time() - locklib._STALE_AFTER - 5
        os.utime(str(lock_file), (old_time, old_time))
        assert not locklib.is_locked("theta")
