"""Tests for envault.metrics."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_metrics import metrics_cmd
from envault.metrics import MetricsError, all_metrics, project_metrics, summary
from envault.storage import save_env

PASS = "test-pass"


@pytest.fixture()
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_STORAGE_DIR", str(tmp_path))
    import envault.storage as st
    monkeypatch.setattr(st, "_BASE_DIR", tmp_path)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def seeded(tmp_storage):
    save_env("alpha", {"KEY_A": "1", "KEY_B": "2"}, PASS)
    save_env("beta", {"ONLY": "x"}, PASS)
    return tmp_storage


class TestProjectMetrics:
    def test_key_count(self, seeded):
        m = project_metrics("alpha", PASS)
        assert m.key_count == 2

    def test_keys_sorted(self, seeded):
        m = project_metrics("alpha", PASS)
        assert m.keys == ["KEY_A", "KEY_B"]

    def test_size_bytes_positive(self, seeded):
        m = project_metrics("alpha", PASS)
        assert m.size_bytes > 0

    def test_last_modified_is_iso(self, seeded):
        m = project_metrics("alpha", PASS)
        assert "T" in m.last_modified  # ISO-8601 contains 'T'

    def test_missing_project_raises(self, tmp_storage):
        with pytest.raises(MetricsError, match="not found"):
            project_metrics("ghost", PASS)

    def test_empty_name_raises(self, tmp_storage):
        with pytest.raises(MetricsError, match="empty"):
            project_metrics("", PASS)


class TestAllMetricsAndSummary:
    def test_returns_all_projects(self, seeded):
        results = all_metrics(PASS)
        names = [m.project for m in results]
        assert "alpha" in names and "beta" in names

    def test_sorted_alphabetically(self, seeded):
        results = all_metrics(PASS)
        names = [m.project for m in results]
        assert names == sorted(names)

    def test_summary_totals(self, seeded):
        results = all_metrics(PASS)
        totals = summary(results)
        assert totals["total_projects"] == 2
        assert totals["total_keys"] == 3
        assert totals["total_bytes"] > 0

    def test_empty_storage_returns_empty(self, tmp_storage):
        results = all_metrics(PASS)
        assert results == []


class TestMetricsCLI:
    def test_show_command(self, seeded, runner):
        result = runner.invoke(metrics_cmd, ["show", "alpha", "--passphrase", PASS])
        assert result.exit_code == 0
        assert "Keys" in result.output
        assert "alpha" in result.output

    def test_show_with_keys_flag(self, seeded, runner):
        result = runner.invoke(metrics_cmd, ["show", "alpha", "--passphrase", PASS, "--keys"])
        assert result.exit_code == 0
        assert "KEY_A" in result.output

    def test_show_missing_project(self, tmp_storage, runner):
        result = runner.invoke(metrics_cmd, ["show", "nope", "--passphrase", PASS])
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_summary_command(self, seeded, runner):
        result = runner.invoke(metrics_cmd, ["summary", "--passphrase", PASS])
        assert result.exit_code == 0
        assert "Projects" in result.output
        assert "alpha" in result.output
        assert "beta" in result.output

    def test_summary_empty(self, tmp_storage, runner):
        result = runner.invoke(metrics_cmd, ["summary", "--passphrase", PASS])
        assert result.exit_code == 0
        assert "No projects" in result.output
