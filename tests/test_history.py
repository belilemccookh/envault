"""Tests for envault.history and envault.cli_history."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_history import history_cmd
from envault.history import (
    _MAX_SNAPSHOTS,
    clear_history,
    get_snapshot,
    list_snapshots,
    record_snapshot,
)


@pytest.fixture()
def tmp_storage(tmp_path, monkeypatch):
    """Redirect storage root to a temp directory."""
    import envault.storage as st
    import envault.history as hs

    monkeypatch.setattr(st, "_BASE_DIR", tmp_path)
    monkeypatch.setattr(hs, "_project_path", st._project_path)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


class TestRecordAndList:
    def test_empty_history(self, tmp_storage):
        assert list_snapshots("proj") == []

    def test_record_creates_entry(self, tmp_storage):
        record_snapshot("proj", {"KEY": "val"}, note="initial")
        snaps = list_snapshots("proj")
        assert len(snaps) == 1
        assert snaps[0]["env"] == {"KEY": "val"}
        assert snaps[0]["note"] == "initial"
        assert "timestamp" in snaps[0]

    def test_multiple_snapshots_ordered(self, tmp_storage):
        for i in range(3):
            record_snapshot("proj", {"K": str(i)})
        snaps = list_snapshots("proj")
        assert [s["env"]["K"] for s in snaps] == ["0", "1", "2"]

    def test_max_snapshots_enforced(self, tmp_storage):
        for i in range(_MAX_SNAPSHOTS + 5):
            record_snapshot("proj", {"i": str(i)})
        assert len(list_snapshots("proj")) == _MAX_SNAPSHOTS


class TestGetSnapshot:
    def test_get_latest(self, tmp_storage):
        record_snapshot("proj", {"A": "1"})
        record_snapshot("proj", {"A": "2"})
        assert get_snapshot("proj", -1) == {"A": "2"}

    def test_get_by_index(self, tmp_storage):
        record_snapshot("proj", {"A": "first"})
        record_snapshot("proj", {"A": "second"})
        assert get_snapshot("proj", 0) == {"A": "first"}

    def test_raises_on_empty(self, tmp_storage):
        with pytest.raises(IndexError):
            get_snapshot("missing", 0)


class TestClearHistory:
    def test_clear_returns_count(self, tmp_storage):
        record_snapshot("proj", {"X": "1"})
        record_snapshot("proj", {"X": "2"})
        assert clear_history("proj") == 2
        assert list_snapshots("proj") == []

    def test_clear_nonexistent_returns_zero(self, tmp_storage):
        assert clear_history("ghost") == 0


class TestCLIHistory:
    def test_list_no_history(self, tmp_storage, runner):
        result = runner.invoke(history_cmd, ["list", "proj"])
        assert result.exit_code == 0
        assert "No history" in result.output

    def test_list_shows_entries(self, tmp_storage, runner):
        record_snapshot("proj", {"A": "1", "B": "2"})
        result = runner.invoke(history_cmd, ["list", "proj"])
        assert result.exit_code == 0
        assert "2 keys" in result.output

    def test_show_latest(self, tmp_storage, runner):
        record_snapshot("proj", {"FOO": "bar"})
        result = runner.invoke(history_cmd, ["show", "proj"])
        assert result.exit_code == 0
        assert "FOO=bar" in result.output

    def test_clear_with_yes_flag(self, tmp_storage, runner):
        record_snapshot("proj", {"K": "v"})
        result = runner.invoke(history_cmd, ["clear", "proj", "--yes"])
        assert result.exit_code == 0
        assert "Cleared 1" in result.output
