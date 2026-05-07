"""Integration tests wiring favorites into the main CLI entry-point."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli import cli


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    import envault.storage as _storage
    monkeypatch.setattr(_storage, "BASE_DIR", tmp_path)
    yield tmp_path


def test_favorites_add_via_main_cli(runner):
    """favorites add is reachable through the top-level CLI."""
    result = runner.invoke(cli, ["favorites", "add", "integration-proj"])
    assert result.exit_code == 0
    assert "integration-proj" in result.output


def test_favorites_list_via_main_cli(runner):
    runner.invoke(cli, ["favorites", "add", "proj-a"])
    runner.invoke(cli, ["favorites", "add", "proj-b"])
    result = runner.invoke(cli, ["favorites", "list"])
    assert result.exit_code == 0
    assert "proj-a" in result.output
    assert "proj-b" in result.output


def test_favorites_clear_then_list_empty(runner):
    runner.invoke(cli, ["favorites", "add", "tmp"])
    runner.invoke(cli, ["favorites", "clear"])
    result = runner.invoke(cli, ["favorites", "list"])
    assert "No favorites" in result.output
