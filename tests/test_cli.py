"""Tests for the envault CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from envault.cli import cli

PASSPHRASE = "test-pass"
PROJECT = "myapp"
ENV_CONTENT = b"API_KEY=secret\nDEBUG=true\n"


@pytest.fixture()
def runner():
    return CliRunner()


class TestSetCommand:
    def test_set_stores_env(self, runner, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_bytes(ENV_CONTENT)

        with patch("envault.cli.save_env") as mock_save:
            result = runner.invoke(
                cli,
                ["set", PROJECT, "--file", str(env_file),
                 "--passphrase", PASSPHRASE, "--passphrase", PASSPHRASE],
            )
        assert result.exit_code == 0
        assert f"Stored env for project '{PROJECT}'" in result.output
        mock_save.assert_called_once_with(PROJECT, ENV_CONTENT, PASSPHRASE)

    def test_set_missing_file(self, runner, tmp_path):
        result = runner.invoke(
            cli,
            ["set", PROJECT, "--file", str(tmp_path / "missing.env"),
             "--passphrase", PASSPHRASE, "--passphrase", PASSPHRASE],
        )
        assert result.exit_code != 0
        assert "not found" in result.output


class TestGetCommand:
    def test_get_writes_file(self, runner, tmp_path):
        output = tmp_path / ".env"

        with patch("envault.cli.load_env", return_value=ENV_CONTENT):
            result = runner.invoke(
                cli,
                ["get", PROJECT, "--output", str(output),
                 "--passphrase", PASSPHRASE],
            )
        assert result.exit_code == 0
        assert output.read_bytes() == ENV_CONTENT

    def test_get_unknown_project(self, runner, tmp_path):
        with patch("envault.cli.load_env", side_effect=KeyError(PROJECT)):
            result = runner.invoke(
                cli,
                ["get", PROJECT, "--output", str(tmp_path / ".env"),
                 "--passphrase", PASSPHRASE],
            )
        assert result.exit_code != 0
        assert "no stored env" in result.output


class TestListCommand:
    def test_list_shows_projects(self, runner):
        with patch("envault.cli.list_projects", return_value=["proj_a", "proj_b"]):
            result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "proj_a" in result.output
        assert "proj_b" in result.output

    def test_list_empty(self, runner):
        with patch("envault.cli.list_projects", return_value=[]):
            result = runner.invoke(cli, ["list"])
        assert "No projects stored yet" in result.output


class TestDeleteCommand:
    def test_delete_success(self, runner):
        with patch("envault.cli.delete_env") as mock_del:
            result = runner.invoke(cli, ["delete", PROJECT, "--yes"])
        assert result.exit_code == 0
        assert "Deleted" in result.output
        mock_del.assert_called_once_with(PROJECT)

    def test_delete_unknown(self, runner):
        with patch("envault.cli.delete_env", side_effect=KeyError(PROJECT)):
            result = runner.invoke(cli, ["delete", PROJECT, "--yes"])
        assert result.exit_code != 0
        assert "no stored env" in result.output
