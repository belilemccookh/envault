"""CLI tests for webhook commands."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_webhooks import webhooks_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def tmp_storage(tmp_path: Path) -> Path:
    return tmp_path


class TestAddCommand:
    def test_add_success(self, runner: CliRunner, tmp_storage: Path) -> None:
        with patch("envault.cli_webhooks.register") as mock_reg:
            result = runner.invoke(
                webhooks_cmd, ["add", "myproject", "https://example.com/hook"]
            )
        assert result.exit_code == 0
        assert "registered" in result.output
        mock_reg.assert_called_once_with("myproject", "https://example.com/hook")

    def test_add_invalid_url_shows_error(self, runner: CliRunner) -> None:
        from envault.webhooks import WebhookError

        with patch(
            "envault.cli_webhooks.register", side_effect=WebhookError("Invalid URL scheme: ftp://x")
        ):
            result = runner.invoke(webhooks_cmd, ["add", "myproject", "ftp://x"])
        assert result.exit_code != 0
        assert "Invalid URL scheme" in result.output


class TestRemoveCommand:
    def test_remove_present(self, runner: CliRunner) -> None:
        with patch("envault.cli_webhooks.unregister", return_value=True):
            result = runner.invoke(
                webhooks_cmd, ["remove", "myproject", "https://example.com/hook"]
            )
        assert result.exit_code == 0
        assert "Removed" in result.output

    def test_remove_missing(self, runner: CliRunner) -> None:
        with patch("envault.cli_webhooks.unregister", return_value=False):
            result = runner.invoke(
                webhooks_cmd, ["remove", "myproject", "https://missing.example.com"]
            )
        assert result.exit_code == 0
        assert "not found" in result.output


class TestListCommand:
    def test_list_empty(self, runner: CliRunner) -> None:
        with patch("envault.cli_webhooks.list_hooks", return_value=[]):
            result = runner.invoke(webhooks_cmd, ["list", "myproject"])
        assert result.exit_code == 0
        assert "No webhooks" in result.output

    def test_list_shows_urls(self, runner: CliRunner) -> None:
        urls = ["https://a.example.com", "https://b.example.com"]
        with patch("envault.cli_webhooks.list_hooks", return_value=urls):
            result = runner.invoke(webhooks_cmd, ["list", "myproject"])
        assert "https://a.example.com" in result.output
        assert "https://b.example.com" in result.output


class TestFireCommand:
    def test_fire_no_hooks(self, runner: CliRunner) -> None:
        with patch("envault.cli_webhooks.notify", return_value=[]):
            result = runner.invoke(webhooks_cmd, ["fire", "myproject", "env.updated"])
        assert result.exit_code == 0
        assert "No webhooks" in result.output

    def test_fire_shows_results(self, runner: CliRunner) -> None:
        results = [("https://example.com", True, "200")]
        with patch("envault.cli_webhooks.notify", return_value=results):
            result = runner.invoke(webhooks_cmd, ["fire", "myproject", "env.updated"])
        assert result.exit_code == 0
        assert "https://example.com" in result.output
        assert "200" in result.output
