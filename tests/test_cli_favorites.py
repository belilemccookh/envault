"""CLI integration tests for the favorites commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_favorites import favorites_cmd


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    import envault.storage as _storage
    monkeypatch.setattr(_storage, "BASE_DIR", tmp_path)
    yield tmp_path


class TestAddCommand:
    def test_add_success(self, runner):
        result = runner.invoke(favorites_cmd, ["add", "myproject"])
        assert result.exit_code == 0
        assert "Added 'myproject'" in result.output

    def test_add_empty_shows_error(self, runner):
        result = runner.invoke(favorites_cmd, ["add", ""])
        assert result.exit_code != 0
        assert "Error" in result.output or "Error" in (result.stderr or "")


class TestRemoveCommand:
    def test_remove_success(self, runner):
        runner.invoke(favorites_cmd, ["add", "proj"])
        result = runner.invoke(favorites_cmd, ["remove", "proj"])
        assert result.exit_code == 0
        assert "Removed 'proj'" in result.output

    def test_remove_nonexistent_shows_error(self, runner):
        result = runner.invoke(favorites_cmd, ["remove", "ghost"])
        assert result.exit_code != 0


class TestListCommand:
    def test_list_empty(self, runner):
        result = runner.invoke(favorites_cmd, ["list"])
        assert result.exit_code == 0
        assert "No favorites" in result.output

    def test_list_shows_projects(self, runner):
        runner.invoke(favorites_cmd, ["add", "alpha"])
        runner.invoke(favorites_cmd, ["add", "beta"])
        result = runner.invoke(favorites_cmd, ["list"])
        assert "alpha" in result.output
        assert "beta" in result.output


class TestCheckCommand:
    def test_check_is_favorite(self, runner):
        runner.invoke(favorites_cmd, ["add", "proj"])
        result = runner.invoke(favorites_cmd, ["check", "proj"])
        assert result.exit_code == 0
        assert "is a favorite" in result.output

    def test_check_not_favorite(self, runner):
        result = runner.invoke(favorites_cmd, ["check", "unknown"])
        assert result.exit_code == 0
        assert "NOT" in result.output


class TestClearCommand:
    def test_clear_reports_count(self, runner):
        runner.invoke(favorites_cmd, ["add", "a"])
        runner.invoke(favorites_cmd, ["add", "b"])
        result = runner.invoke(favorites_cmd, ["clear"])
        assert result.exit_code == 0
        assert "2" in result.output

    def test_clear_empty(self, runner):
        result = runner.invoke(favorites_cmd, ["clear"])
        assert result.exit_code == 0
        assert "0" in result.output
