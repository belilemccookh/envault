"""CLI integration tests for the groups command."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_groups import groups_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.groups._base_dir", lambda: tmp_path)
    return tmp_path


class TestAddCommand:
    def test_add_success(self, runner):
        result = runner.invoke(groups_cmd, ["add", "backend", "api"])
        assert result.exit_code == 0
        assert "api" in result.output
        assert "backend" in result.output

    def test_add_empty_group_shows_error(self, runner):
        result = runner.invoke(groups_cmd, ["add", "", "api"])
        assert result.exit_code != 0
        assert "Error" in result.output


class TestRemoveCommand:
    def test_remove_success(self, runner):
        runner.invoke(groups_cmd, ["add", "backend", "api"])
        result = runner.invoke(groups_cmd, ["remove", "backend", "api"])
        assert result.exit_code == 0
        assert "Removed" in result.output

    def test_remove_missing_project_shows_error(self, runner):
        runner.invoke(groups_cmd, ["add", "backend", "api"])
        result = runner.invoke(groups_cmd, ["remove", "backend", "ghost"])
        assert result.exit_code != 0
        assert "Error" in result.output


class TestListCommand:
    def test_list_empty(self, runner):
        result = runner.invoke(groups_cmd, ["list"])
        assert result.exit_code == 0
        assert "No groups" in result.output

    def test_list_shows_groups(self, runner):
        runner.invoke(groups_cmd, ["add", "backend", "api"])
        runner.invoke(groups_cmd, ["add", "frontend", "web"])
        result = runner.invoke(groups_cmd, ["list"])
        assert "backend" in result.output
        assert "frontend" in result.output


class TestShowCommand:
    def test_show_existing(self, runner):
        runner.invoke(groups_cmd, ["add", "backend", "api"])
        result = runner.invoke(groups_cmd, ["show", "backend"])
        assert result.exit_code == 0
        assert "api" in result.output

    def test_show_missing_shows_error(self, runner):
        result = runner.invoke(groups_cmd, ["show", "ghost"])
        assert result.exit_code != 0
        assert "Error" in result.output


class TestDeleteCommand:
    def test_delete_success(self, runner):
        runner.invoke(groups_cmd, ["add", "temp", "svc"])
        result = runner.invoke(groups_cmd, ["delete", "temp"])
        assert result.exit_code == 0
        assert "deleted" in result.output

    def test_delete_missing_shows_error(self, runner):
        result = runner.invoke(groups_cmd, ["delete", "nope"])
        assert result.exit_code != 0
        assert "Error" in result.output
