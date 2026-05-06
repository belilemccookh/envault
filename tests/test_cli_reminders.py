"""CLI tests for envault.cli_reminders."""
from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest
from click.testing import CliRunner

from envault.cli_reminders import reminders_cmd
import envault.reminders as rem


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.storage._base_dir", lambda: tmp_path)
    monkeypatch.setattr("envault.reminders._reminders_path", lambda: tmp_path / "reminders.json")
    yield tmp_path


class TestSetCommand:
    def test_set_success(self, runner):
        result = runner.invoke(reminders_cmd, ["set", "myapp", "--days", "14"])
        assert result.exit_code == 0
        assert "myapp" in result.output

    def test_set_invalid_days(self, runner):
        result = runner.invoke(reminders_cmd, ["set", "myapp", "--days", "-1"])
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_set_with_note(self, runner):
        result = runner.invoke(reminders_cmd, ["set", "myapp", "--days", "7", "--note", "urgent"])
        assert result.exit_code == 0
        entry = rem.get_reminder("myapp")
        assert entry["note"] == "urgent"


class TestShowCommand:
    def test_show_existing(self, runner):
        rem.set_reminder("proj", 5)
        result = runner.invoke(reminders_cmd, ["show", "proj"])
        assert result.exit_code == 0
        assert "proj" in result.output
        assert "Due" in result.output

    def test_show_missing(self, runner):
        result = runner.invoke(reminders_cmd, ["show", "ghost"])
        assert result.exit_code == 0
        assert "No reminder" in result.output


class TestListCommand:
    def test_list_empty(self, runner):
        result = runner.invoke(reminders_cmd, ["list"])
        assert result.exit_code == 0
        assert "No reminders" in result.output

    def test_list_shows_projects(self, runner):
        rem.set_reminder("alpha", 3)
        rem.set_reminder("beta", 10)
        result = runner.invoke(reminders_cmd, ["list"])
        assert "alpha" in result.output
        assert "beta" in result.output

    def test_due_only_flag(self, runner, tmp_path):
        past = (datetime.utcnow() - timedelta(days=1)).isoformat(timespec="seconds")
        data = {"old": {"project": "old", "due": past, "note": "", "created": past}}
        (tmp_path / "reminders.json").write_text(json.dumps(data))
        rem.set_reminder("future", 30)
        result = runner.invoke(reminders_cmd, ["list", "--due-only"])
        assert "old" in result.output
        assert "future" not in result.output


class TestDeleteCommand:
    def test_delete_existing(self, runner):
        rem.set_reminder("proj", 7)
        result = runner.invoke(reminders_cmd, ["delete", "proj"])
        assert result.exit_code == 0
        assert "deleted" in result.output
        assert rem.get_reminder("proj") is None

    def test_delete_missing(self, runner):
        result = runner.invoke(reminders_cmd, ["delete", "nope"])
        assert result.exit_code == 0
        assert "No reminder found" in result.output
