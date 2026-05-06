"""CLI integration tests for the alias sub-commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_aliases import aliases_cmd


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    import envault.storage as st
    import envault.aliases as al

    monkeypatch.setattr(st, "_base_dir", lambda: tmp_path)
    monkeypatch.setattr(al, "_base_dir", lambda: tmp_path)
    yield tmp_path


class TestSetCommand:
    def test_set_success(self, runner):
        result = runner.invoke(aliases_cmd, ["set", "prod", "production-env"])
        assert result.exit_code == 0
        assert "prod" in result.output
        assert "production-env" in result.output

    def test_set_invalid_alias_shows_error(self, runner):
        result = runner.invoke(aliases_cmd, ["set", "bad/alias", "project"])
        assert result.exit_code != 0
        assert "Error" in result.output or "Error" in (result.stderr or "")


class TestRemoveCommand:
    def test_remove_existing(self, runner):
        runner.invoke(aliases_cmd, ["set", "tmp", "temp-proj"])
        result = runner.invoke(aliases_cmd, ["remove", "tmp"])
        assert result.exit_code == 0
        assert "removed" in result.output

    def test_remove_nonexistent_exits_nonzero(self, runner):
        result = runner.invoke(aliases_cmd, ["remove", "ghost"])
        assert result.exit_code != 0


class TestShowCommand:
    def test_show_known_alias(self, runner):
        runner.invoke(aliases_cmd, ["set", "svc", "my-service"])
        result = runner.invoke(aliases_cmd, ["show", "svc"])
        assert result.exit_code == 0
        assert "my-service" in result.output

    def test_show_unknown_exits_nonzero(self, runner):
        result = runner.invoke(aliases_cmd, ["show", "nope"])
        assert result.exit_code != 0


class TestListCommand:
    def test_list_empty(self, runner):
        result = runner.invoke(aliases_cmd, ["list"])
        assert result.exit_code == 0
        assert "No aliases" in result.output

    def test_list_shows_entries(self, runner):
        runner.invoke(aliases_cmd, ["set", "a", "alpha"])
        runner.invoke(aliases_cmd, ["set", "b", "beta"])
        result = runner.invoke(aliases_cmd, ["list"])
        assert result.exit_code == 0
        assert "alpha" in result.output
        assert "beta" in result.output
