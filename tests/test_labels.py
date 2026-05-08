"""Tests for envault.labels and envault.cli_labels."""
from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.labels import (
    LabelError,
    add_label,
    remove_label,
    get_labels,
    find_by_label,
    clear_labels,
)
from envault.cli_labels import labels_cmd


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_storage(tmp_path):
    os.environ["ENVAULT_STORAGE"] = str(tmp_path)
    yield str(tmp_path)
    del os.environ["ENVAULT_STORAGE"]


@pytest.fixture()
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Unit tests – label library
# ---------------------------------------------------------------------------

class TestAddLabel:
    def test_add_single(self, tmp_storage):
        labels = add_label(tmp_storage, "proj", "production")
        assert "production" in labels

    def test_add_multiple(self, tmp_storage):
        add_label(tmp_storage, "proj", "production")
        labels = add_label(tmp_storage, "proj", "critical")
        assert labels == ["production", "critical"]

    def test_add_idempotent(self, tmp_storage):
        add_label(tmp_storage, "proj", "production")
        labels = add_label(tmp_storage, "proj", "production")
        assert labels.count("production") == 1

    def test_empty_project_raises(self, tmp_storage):
        with pytest.raises(LabelError):
            add_label(tmp_storage, "", "production")

    def test_empty_label_raises(self, tmp_storage):
        with pytest.raises(LabelError):
            add_label(tmp_storage, "proj", "   ")


class TestRemoveLabel:
    def test_removes_existing(self, tmp_storage):
        add_label(tmp_storage, "proj", "staging")
        labels = remove_label(tmp_storage, "proj", "staging")
        assert "staging" not in labels

    def test_remove_nonexistent_is_noop(self, tmp_storage):
        labels = remove_label(tmp_storage, "proj", "ghost")
        assert labels == []


class TestGetLabels:
    def test_returns_empty_for_unknown_project(self, tmp_storage):
        assert get_labels(tmp_storage, "unknown") == []

    def test_returns_all_labels(self, tmp_storage):
        add_label(tmp_storage, "proj", "a")
        add_label(tmp_storage, "proj", "b")
        assert get_labels(tmp_storage, "proj") == ["a", "b"]


class TestFindByLabel:
    def test_finds_across_projects(self, tmp_storage):
        add_label(tmp_storage, "alpha", "prod")
        add_label(tmp_storage, "beta", "prod")
        add_label(tmp_storage, "gamma", "dev")
        projects = find_by_label(tmp_storage, "prod")
        assert set(projects) == {"alpha", "beta"}

    def test_returns_empty_when_none_match(self, tmp_storage):
        assert find_by_label(tmp_storage, "nope") == []


class TestClearLabels:
    def test_removes_all(self, tmp_storage):
        add_label(tmp_storage, "proj", "x")
        clear_labels(tmp_storage, "proj")
        assert get_labels(tmp_storage, "proj") == []

    def test_clear_unknown_project_is_noop(self, tmp_storage):
        clear_labels(tmp_storage, "ghost")  # should not raise


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_cli_add_success(runner, tmp_storage):
    result = runner.invoke(labels_cmd, ["add", "myproject", "production"])
    assert result.exit_code == 0
    assert "production" in result.output


def test_cli_add_empty_label_shows_error(runner, tmp_storage):
    result = runner.invoke(labels_cmd, ["add", "myproject", ""])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_cli_list_labels(runner, tmp_storage):
    add_label(tmp_storage, "myproject", "staging")
    result = runner.invoke(labels_cmd, ["list", "myproject"])
    assert "staging" in result.output


def test_cli_find(runner, tmp_storage):
    add_label(tmp_storage, "alpha", "shared")
    add_label(tmp_storage, "beta", "shared")
    result = runner.invoke(labels_cmd, ["find", "shared"])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_cli_clear(runner, tmp_storage):
    add_label(tmp_storage, "proj", "temp")
    result = runner.invoke(labels_cmd, ["clear", "proj"])
    assert result.exit_code == 0
    assert get_labels(tmp_storage, "proj") == []
