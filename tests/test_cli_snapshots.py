"""Integration tests for the snapshots CLI commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_snapshots import snapshots_cmd
from envault.storage import save_env


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    import envault.storage as st
    monkeypatch.setattr(st, "STORAGE_DIR", tmp_path)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


PASSPHRASE = "test-pass"
ENV = {"KEY": "val", "FOO": "bar"}


@pytest.fixture()
def stored_project(tmp_storage):
    save_env("myapp", ENV, PASSPHRASE)
    return "myapp"


class TestCreateCommand:
    def test_create_success(self, runner, stored_project):
        result = runner.invoke(
            snapshots_cmd,
            ["create", "myapp", "release-1"],
            input=PASSPHRASE + "\n",
        )
        assert result.exit_code == 0
        assert "release-1" in result.output

    def test_create_empty_label_fails(self, runner, stored_project):
        result = runner.invoke(
            snapshots_cmd,
            ["create", "myapp", "   "],
            input=PASSPHRASE + "\n",
        )
        assert result.exit_code != 0


class TestListCommand:
    def test_list_empty(self, runner, stored_project):
        result = runner.invoke(snapshots_cmd, ["list", "myapp"])
        assert result.exit_code == 0
        assert "No snapshots" in result.output

    def test_list_shows_entries(self, runner, stored_project):
        runner.invoke(
            snapshots_cmd,
            ["create", "myapp", "v1"],
            input=PASSPHRASE + "\n",
        )
        result = runner.invoke(snapshots_cmd, ["list", "myapp"])
        assert "v1" in result.output


class TestShowCommand:
    def test_show_displays_env(self, runner, stored_project):
        runner.invoke(
            snapshots_cmd,
            ["create", "myapp", "snap1"],
            input=PASSPHRASE + "\n",
        )
        result = runner.invoke(snapshots_cmd, ["show", "myapp", "1"])
        assert result.exit_code == 0
        assert "KEY=val" in result.output

    def test_show_missing_id(self, runner, stored_project):
        result = runner.invoke(snapshots_cmd, ["show", "myapp", "99"])
        assert result.exit_code != 0
        assert "not found" in result.output


class TestDeleteCommand:
    def test_delete_removes_snapshot(self, runner, stored_project):
        runner.invoke(
            snapshots_cmd,
            ["create", "myapp", "to-delete"],
            input=PASSPHRASE + "\n",
        )
        result = runner.invoke(
            snapshots_cmd,
            ["delete", "myapp", "1"],
            input="y\n",
        )
        assert result.exit_code == 0
        assert "deleted" in result.output
