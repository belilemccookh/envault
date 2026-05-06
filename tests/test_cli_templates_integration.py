"""Integration tests: template CLI wired through the main cli group."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.templates import save_template
from envault.storage import save_env, load_env


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.templates._base_dir", lambda: tmp_path)
    monkeypatch.setattr("envault.storage._base_dir", lambda: tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_template_list_via_main_cli(runner):
    result = runner.invoke(cli, ["template", "list"])
    assert result.exit_code == 0
    assert "No templates" in result.output


def test_template_save_from_project(runner, tmp_path):
    save_env("myapp", {"DB": "postgres", "PORT": "5432"}, passphrase="")
    result = runner.invoke(
        cli,
        ["--passphrase", "", "template", "save", "myapp-tpl", "--from-project", "myapp", "--desc", "My app template"],
    )
    assert result.exit_code == 0
    assert "2 keys" in result.output


def test_template_apply_fills_missing_keys(runner, tmp_path):
    save_template("defaults", {"LOG_LEVEL": "INFO", "TIMEOUT": "30"})
    save_env("svc", {"LOG_LEVEL": "DEBUG"}, passphrase="")
    result = runner.invoke(cli, ["--passphrase", "", "template", "apply", "defaults", "svc"])
    assert result.exit_code == 0
    env = load_env("svc", passphrase="")
    assert env["TIMEOUT"] == "30"
    assert env["LOG_LEVEL"] == "DEBUG"  # existing value preserved


def test_template_delete_via_cli(runner):
    save_template("old", {"X": "1"})
    result = runner.invoke(cli, ["template", "delete", "old"], input="y\n")
    assert result.exit_code == 0
    assert "deleted" in result.output.lower()


def test_template_show_missing_exits_nonzero(runner):
    result = runner.invoke(cli, ["template", "show", "phantom"])
    assert result.exit_code != 0
