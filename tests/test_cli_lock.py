"""Tests for envault.cli_lock CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault import lock as locklib
from envault.cli_lock import lock_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    import envault.storage as st
    monkeypatch.setattr(st, "_BASE", tmp_path)
    import envault.lock as lk
    monkeypatch.setattr(lk, "_project_path", st._project_path)
    yield tmp_path


class TestStatusCommand:
    def test_not_locked(self, runner):
        result = runner.invoke(lock_cmd, ["status", "myapp"])
        assert result.exit_code == 0
        assert "not locked" in result.output

    def test_locked(self, runner):
        locklib.acquire("myapp")
        try:
            result = runner.invoke(lock_cmd, ["status", "myapp"])
            assert result.exit_code == 0
            assert "locked" in result.output
        finally:
            locklib.release("myapp")


class TestReleaseCommand:
    def test_release_existing_lock(self, runner):
        locklib.acquire("proj")
        result = runner.invoke(lock_cmd, ["release", "proj"])
        assert result.exit_code == 0
        assert "released" in result.output
        assert not locklib.is_locked("proj")

    def test_release_not_locked(self, runner):
        result = runner.invoke(lock_cmd, ["release", "ghost"])
        assert result.exit_code == 0
        assert "nothing to do" in result.output


class TestListCommand:
    def test_no_locked_projects(self, runner):
        result = runner.invoke(lock_cmd, ["list"])
        assert result.exit_code == 0
        assert "No projects" in result.output

    def test_shows_locked_project(self, runner):
        from envault.storage import save_env
        save_env("service", {"K": "V"}, "pass")
        locklib.acquire("service")
        try:
            result = runner.invoke(lock_cmd, ["list"])
            assert result.exit_code == 0
            assert "service" in result.output
        finally:
            locklib.release("service")
