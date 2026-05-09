"""Tests for envault.dependencies and envault.cli_dependencies."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_dependencies import deps_cmd
from envault.dependencies import (
    DependencyError,
    add_dependency,
    all_dependencies,
    list_dependencies,
    list_dependents,
    remove_dependency,
)


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.dependencies.DATA_DIR", tmp_path)
    yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Library tests
# ---------------------------------------------------------------------------

class TestAddDependency:
    def test_add_single(self):
        deps = add_dependency("app", "db")
        assert deps == ["db"]

    def test_add_multiple(self):
        add_dependency("app", "db")
        deps = add_dependency("app", "cache")
        assert "db" in deps and "cache" in deps

    def test_add_idempotent(self):
        add_dependency("app", "db")
        deps = add_dependency("app", "db")
        assert deps.count("db") == 1

    def test_self_dependency_raises(self):
        with pytest.raises(DependencyError, match="cannot depend on itself"):
            add_dependency("app", "app")

    def test_empty_project_raises(self):
        with pytest.raises(DependencyError):
            add_dependency("", "db")

    def test_empty_dep_raises(self):
        with pytest.raises(DependencyError):
            add_dependency("app", "")


class TestRemoveDependency:
    def test_remove_existing(self):
        add_dependency("app", "db")
        deps = remove_dependency("app", "db")
        assert "db" not in deps

    def test_remove_nonexistent_raises(self):
        with pytest.raises(DependencyError, match="not a dependency"):
            remove_dependency("app", "db")


class TestListAndDependents:
    def test_list_dependencies(self):
        add_dependency("app", "db")
        add_dependency("app", "cache")
        assert set(list_dependencies("app")) == {"db", "cache"}

    def test_list_empty(self):
        assert list_dependencies("unknown") == []

    def test_list_dependents(self):
        add_dependency("app", "db")
        add_dependency("worker", "db")
        assert set(list_dependents("db")) == {"app", "worker"}

    def test_all_dependencies(self):
        add_dependency("app", "db")
        add_dependency("worker", "cache")
        data = all_dependencies()
        assert "app" in data and "worker" in data


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

class TestDepsCmd:
    def test_add_success(self, runner):
        result = runner.invoke(deps_cmd, ["add", "app", "db"])
        assert result.exit_code == 0
        assert "db" in result.output

    def test_add_self_shows_error(self, runner):
        result = runner.invoke(deps_cmd, ["add", "app", "app"])
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_list_cmd(self, runner):
        add_dependency("app", "db")
        result = runner.invoke(deps_cmd, ["list", "app"])
        assert "db" in result.output

    def test_list_empty(self, runner):
        result = runner.invoke(deps_cmd, ["list", "ghost"])
        assert "no dependencies" in result.output

    def test_dependents_cmd(self, runner):
        add_dependency("app", "db")
        result = runner.invoke(deps_cmd, ["dependents", "db"])
        assert "app" in result.output

    def test_all_cmd_empty(self, runner):
        result = runner.invoke(deps_cmd, ["all"])
        assert "No dependencies" in result.output

    def test_remove_cmd(self, runner):
        add_dependency("app", "db")
        result = runner.invoke(deps_cmd, ["remove", "app", "db"])
        assert result.exit_code == 0
        assert "Removed" in result.output
