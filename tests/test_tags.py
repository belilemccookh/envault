"""Tests for envault.tags and envault.cli_tags."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_tags import tags_cmd
from envault import tags as tag_lib


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    """Redirect storage base dir to a temp directory."""
    monkeypatch.setattr("envault.tags._base_dir", lambda: tmp_path)
    yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Unit tests for tags module
# ---------------------------------------------------------------------------

class TestTagLib:
    def test_add_and_get(self):
        tag_lib.add_tag("alpha", "production")
        assert "production" in tag_lib.get_tags("alpha")

    def test_add_normalises_case(self):
        tag_lib.add_tag("alpha", "  Staging  ")
        assert "staging" in tag_lib.get_tags("alpha")

    def test_add_idempotent(self):
        tag_lib.add_tag("alpha", "production")
        tag_lib.add_tag("alpha", "production")
        assert tag_lib.get_tags("alpha").count("production") == 1

    def test_remove_existing(self):
        tag_lib.add_tag("alpha", "production")
        removed = tag_lib.remove_tag("alpha", "production")
        assert removed is True
        assert "production" not in tag_lib.get_tags("alpha")

    def test_remove_nonexistent_returns_false(self):
        assert tag_lib.remove_tag("ghost", "nope") is False

    def test_projects_with_tag(self):
        tag_lib.add_tag("alpha", "production")
        tag_lib.add_tag("beta", "production")
        tag_lib.add_tag("gamma", "staging")
        result = tag_lib.projects_with_tag("production")
        assert result == ["alpha", "beta"]

    def test_clear_tags(self):
        tag_lib.add_tag("alpha", "production")
        tag_lib.clear_tags("alpha")
        assert tag_lib.get_tags("alpha") == []

    def test_all_tags_empty(self):
        assert tag_lib.all_tags() == {}


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

class TestTagCLI:
    def test_add_cmd(self, runner):
        result = runner.invoke(tags_cmd, ["add", "myproject", "production"])
        assert result.exit_code == 0
        assert "production" in result.output

    def test_list_cmd(self, runner):
        tag_lib.add_tag("myproject", "staging")
        result = runner.invoke(tags_cmd, ["list", "myproject"])
        assert result.exit_code == 0
        assert "staging" in result.output

    def test_list_no_tags(self, runner):
        result = runner.invoke(tags_cmd, ["list", "empty"])
        assert result.exit_code == 0
        assert "No tags" in result.output

    def test_remove_cmd(self, runner):
        tag_lib.add_tag("myproject", "production")
        result = runner.invoke(tags_cmd, ["remove", "myproject", "production"])
        assert result.exit_code == 0
        assert "Removed" in result.output

    def test_remove_missing_tag_exits_nonzero(self, runner):
        result = runner.invoke(tags_cmd, ["remove", "myproject", "ghost"])
        assert result.exit_code != 0

    def test_find_cmd(self, runner):
        tag_lib.add_tag("proj1", "production")
        tag_lib.add_tag("proj2", "staging")
        result = runner.invoke(tags_cmd, ["find", "production"])
        assert result.exit_code == 0
        assert "proj1" in result.output
        assert "proj2" not in result.output
