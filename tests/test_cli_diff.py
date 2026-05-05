"""Tests for the envault diff CLI command."""
from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.storage import save_env

PASSPHRASE = "test-pass"


@pytest.fixture()
def runner(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    return CliRunner()


@pytest.fixture()
def stored_project(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    env = "FOO=1\nBAR=old\nKEEP=same\n"
    save_env("myproject", env, PASSPHRASE)
    return tmp_path


class TestDiffCommand:
    def test_diff_against_file_no_changes(self, runner, stored_project, tmp_path):
        env_file = tmp_path / "current.env"
        env_file.write_text("BAR=old\nFOO=1\nKEEP=same\n")
        result = runner.invoke(
            cli,
            ["diff", "myproject", "--file", str(env_file), "--passphrase", PASSPHRASE],
        )
        assert result.exit_code == 0
        assert "No differences" in result.output

    def test_diff_against_file_with_changes(self, runner, stored_project, tmp_path):
        env_file = tmp_path / "new.env"
        env_file.write_text("BAR=new\nBAZ=added\nKEEP=same\n")
        result = runner.invoke(
            cli,
            ["diff", "myproject", "--file", str(env_file), "--passphrase", PASSPHRASE],
        )
        assert result.exit_code == 0
        assert "+" in result.output or "-" in result.output or "~" in result.output

    def test_diff_shows_summary(self, runner, stored_project, tmp_path):
        env_file = tmp_path / "changed.env"
        env_file.write_text("BAR=new\nKEEP=same\n")
        result = runner.invoke(
            cli,
            ["diff", "myproject", "--file", str(env_file), "--passphrase", PASSPHRASE],
        )
        assert result.exit_code == 0
        assert "Summary" in result.output

    def test_diff_masks_values_by_default(self, runner, stored_project, tmp_path):
        env_file = tmp_path / "changed.env"
        env_file.write_text("BAR=new\nKEEP=same\n")
        result = runner.invoke(
            cli,
            ["diff", "myproject", "--file", str(env_file), "--passphrase", PASSPHRASE],
        )
        assert "***" in result.output

    def test_diff_show_values_flag(self, runner, stored_project, tmp_path):
        env_file = tmp_path / "changed.env"
        env_file.write_text("BAR=new\nKEEP=same\n")
        result = runner.invoke(
            cli,
            [
                "diff", "myproject",
                "--file", str(env_file),
                "--passphrase", PASSPHRASE,
                "--show-values",
            ],
        )
        assert "***" not in result.output

    def test_diff_requires_file_or_against(self, runner, stored_project):
        result = runner.invoke(
            cli, ["diff", "myproject", "--passphrase", PASSPHRASE]
        )
        assert result.exit_code != 0

    def test_diff_rejects_both_options(self, runner, stored_project, tmp_path):
        env_file = tmp_path / "f.env"
        env_file.write_text("X=1\n")
        result = runner.invoke(
            cli,
            [
                "diff", "myproject",
                "--file", str(env_file),
                "--against", "other",
                "--passphrase", PASSPHRASE,
            ],
        )
        assert result.exit_code != 0
