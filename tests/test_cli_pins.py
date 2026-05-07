"""CLI integration tests for the pins commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_pins import pins_cmd
from envault.pins import pin_key


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.storage._base_dir", lambda: tmp_path)
    monkeypatch.setattr("envault.pins._base_dir", lambda: tmp_path)


class TestAddCommand:
    def test_add_success(self, runner):
        result = runner.invoke(pins_cmd, ["add", "myapp", "SECRET"])
        assert result.exit_code == 0
        assert "Pinned 'SECRET'" in result.output

    def test_add_empty_key_shows_error(self, runner):
        result = runner.invoke(pins_cmd, ["add", "myapp", ""])
        assert result.exit_code != 0
        assert "Error" in result.output


class TestRemoveCommand:
    def test_remove_existing(self, runner):
        pin_key("myapp", "TOKEN")
        result = runner.invoke(pins_cmd, ["remove", "myapp", "TOKEN"])
        assert result.exit_code == 0
        assert "Unpinned" in result.output

    def test_remove_nonexistent(self, runner):
        result = runner.invoke(pins_cmd, ["remove", "myapp", "GHOST"])
        assert result.exit_code == 0
        assert "not pinned" in result.output


class TestListCommand:
    def test_list_shows_pins(self, runner):
        pin_key("myapp", "DB_URL")
        pin_key("myapp", "API_KEY")
        result = runner.invoke(pins_cmd, ["list", "myapp"])
        assert "DB_URL" in result.output
        assert "API_KEY" in result.output

    def test_list_empty_project(self, runner):
        result = runner.invoke(pins_cmd, ["list", "empty_proj"])
        assert "No pinned keys" in result.output


class TestCheckCommand:
    def test_check_pinned(self, runner):
        pin_key("myapp", "PASS")
        result = runner.invoke(pins_cmd, ["check", "myapp", "PASS"])
        assert "is pinned" in result.output

    def test_check_not_pinned(self, runner):
        result = runner.invoke(pins_cmd, ["check", "myapp", "MISSING"])
        assert "NOT pinned" in result.output


class TestAllCommand:
    def test_all_shows_projects(self, runner):
        pin_key("alpha", "K1")
        pin_key("beta", "K2")
        result = runner.invoke(pins_cmd, ["all"])
        assert "alpha" in result.output
        assert "beta" in result.output

    def test_all_empty(self, runner):
        result = runner.invoke(pins_cmd, ["all"])
        assert "No pins defined" in result.output
