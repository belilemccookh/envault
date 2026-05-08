"""Tests for envault.activity."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from pathlib import Path

from envault.activity import (
    ActivityError,
    all_activity,
    get_activity,
    record_activity,
    reset_activity,
)
from envault.cli_activity import activity_cmd


@pytest.fixture()
def tmp_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("envault.activity._base_path", lambda: tmp_path)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Library tests
# ---------------------------------------------------------------------------

class TestRecordActivity:
    def test_increments_write(self, tmp_storage):
        entry = record_activity("myapp", "write")
        assert entry["write"] == 1
        assert entry["read"] == 0

    def test_increments_multiple(self, tmp_storage):
        record_activity("myapp", "read")
        record_activity("myapp", "read")
        entry = record_activity("myapp", "write")
        assert entry["read"] == 2
        assert entry["write"] == 1

    def test_last_seen_set(self, tmp_storage):
        entry = record_activity("myapp", "delete")
        assert entry["last_seen"] is not None

    def test_empty_project_raises(self, tmp_storage):
        with pytest.raises(ActivityError, match="empty"):
            record_activity("", "read")

    def test_invalid_action_raises(self, tmp_storage):
        with pytest.raises(ActivityError, match="action"):
            record_activity("myapp", "explode")

    def test_persists_across_calls(self, tmp_storage):
        record_activity("proj", "write")
        entry = get_activity("proj")
        assert entry["write"] == 1


class TestGetActivity:
    def test_unknown_project_returns_zeros(self, tmp_storage):
        entry = get_activity("ghost")
        assert entry == {"read": 0, "write": 0, "delete": 0, "last_seen": None}

    def test_empty_project_raises(self, tmp_storage):
        with pytest.raises(ActivityError):
            get_activity("")


class TestResetActivity:
    def test_removes_entry(self, tmp_storage):
        record_activity("proj", "read")
        reset_activity("proj")
        assert get_activity("proj")["read"] == 0

    def test_reset_nonexistent_is_noop(self, tmp_storage):
        reset_activity("ghost")  # should not raise


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

class TestActivityCLI:
    def test_show_unknown_project(self, tmp_storage, runner):
        result = runner.invoke(activity_cmd, ["show", "ghost"])
        assert result.exit_code == 0
        assert "reads" in result.output

    def test_list_empty(self, tmp_storage, runner):
        result = runner.invoke(activity_cmd, ["list"])
        assert "No activity" in result.output

    def test_list_after_record(self, tmp_storage, runner):
        record_activity("alpha", "write")
        result = runner.invoke(activity_cmd, ["list"])
        assert "alpha" in result.output

    def test_reset_via_cli(self, tmp_storage, runner):
        record_activity("beta", "read")
        result = runner.invoke(activity_cmd, ["reset", "beta"], input="y\n")
        assert result.exit_code == 0
        assert get_activity("beta")["read"] == 0
