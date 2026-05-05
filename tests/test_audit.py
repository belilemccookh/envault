"""Tests for envault.audit module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import envault.audit as audit_mod


@pytest.fixture(autouse=True)
def tmp_audit(tmp_path, monkeypatch):
    """Redirect audit log to a temp directory for every test."""
    monkeypatch.setattr(audit_mod, "APP_DIR", tmp_path)
    monkeypatch.setattr(audit_mod, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    yield tmp_path


class TestRecord:
    def test_creates_log_file(self, tmp_audit):
        audit_mod.record("set", "myapp")
        assert (tmp_audit / "audit.log").exists()

    def test_entry_fields(self, tmp_audit):
        audit_mod.record("get", "myapp", detail="DB_URL", success=True)
        line = (tmp_audit / "audit.log").read_text().strip()
        entry = json.loads(line)
        assert entry["action"] == "get"
        assert entry["project"] == "myapp"
        assert entry["detail"] == "DB_URL"
        assert entry["success"] is True
        assert "ts" in entry

    def test_failed_action_recorded(self, tmp_audit):
        audit_mod.record("delete", "ghost", success=False)
        entry = json.loads((tmp_audit / "audit.log").read_text().strip())
        assert entry["success"] is False

    def test_multiple_entries_appended(self, tmp_audit):
        for i in range(3):
            audit_mod.record("set", f"proj{i}")
        lines = (tmp_audit / "audit.log").read_text().splitlines()
        assert len(lines) == 3


class TestReadLog:
    def test_returns_empty_when_no_log(self, tmp_audit):
        assert audit_mod.read_log() == []

    def test_returns_entries_newest_first(self, tmp_audit):
        for proj in ["a", "b", "c"]:
            audit_mod.record("set", proj)
        entries = audit_mod.read_log()
        assert entries[0]["project"] == "c"
        assert entries[-1]["project"] == "a"

    def test_filter_by_project(self, tmp_audit):
        audit_mod.record("set", "alpha")
        audit_mod.record("set", "beta")
        audit_mod.record("get", "alpha")
        results = audit_mod.read_log(project="alpha")
        assert all(e["project"] == "alpha" for e in results)
        assert len(results) == 2

    def test_limit_respected(self, tmp_audit):
        for i in range(20):
            audit_mod.record("set", "proj")
        assert len(audit_mod.read_log(limit=5)) == 5


class TestTrimLog:
    def test_trim_keeps_max_entries(self, tmp_audit, monkeypatch):
        monkeypatch.setattr(audit_mod, "MAX_ENTRIES", 10)
        for i in range(15):
            audit_mod.record("set", f"p{i}")
        lines = (tmp_audit / "audit.log").read_text().splitlines()
        assert len(lines) == 10
        # Newest entries are kept
        last = json.loads(lines[-1])
        assert last["project"] == "p14"


class TestClearLog:
    def test_clear_removes_file(self, tmp_audit):
        audit_mod.record("set", "proj")
        audit_mod.clear_log()
        assert not (tmp_audit / "audit.log").exists()

    def test_clear_noop_when_missing(self, tmp_audit):
        audit_mod.clear_log()  # Should not raise
