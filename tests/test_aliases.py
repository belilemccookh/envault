"""Tests for envault.aliases."""

from __future__ import annotations

import pytest

from envault.aliases import (
    AliasError,
    clear_aliases,
    list_aliases,
    remove_alias,
    resolve,
    resolve_or_name,
    set_alias,
)


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    """Redirect storage base dir to a temp directory for every test."""
    import envault.storage as st
    import envault.aliases as al

    monkeypatch.setattr(st, "_base_dir", lambda: tmp_path)
    monkeypatch.setattr(al, "_base_dir", lambda: tmp_path)
    yield tmp_path


class TestSetAlias:
    def test_set_and_resolve(self):
        set_alias("myapp", "my-application")
        assert resolve("myapp") == "my-application"

    def test_overwrite_existing(self):
        set_alias("x", "project-a")
        set_alias("x", "project-b")
        assert resolve("x") == "project-b"

    def test_empty_alias_raises(self):
        with pytest.raises(AliasError, match="empty"):
            set_alias("", "project")

    def test_empty_project_raises(self):
        with pytest.raises(AliasError, match="empty"):
            set_alias("alias", "")

    def test_slash_in_alias_raises(self):
        with pytest.raises(AliasError, match="path separators"):
            set_alias("bad/alias", "project")


class TestRemoveAlias:
    def test_remove_existing(self):
        set_alias("tmp", "temp-project")
        remove_alias("tmp")
        assert resolve("tmp") is None

    def test_remove_nonexistent_raises(self):
        with pytest.raises(AliasError, match="not found"):
            remove_alias("ghost")


class TestResolveOrName:
    def test_returns_mapped_project(self):
        set_alias("api", "api-service")
        assert resolve_or_name("api") == "api-service"

    def test_returns_name_when_no_alias(self):
        assert resolve_or_name("unknown-alias") == "unknown-alias"


class TestListAliases:
    def test_empty_when_none_set(self):
        assert list_aliases() == {}

    def test_returns_all_entries(self):
        set_alias("a", "alpha")
        set_alias("b", "beta")
        result = list_aliases()
        assert result == {"a": "alpha", "b": "beta"}

    def test_clear_removes_all(self):
        set_alias("a", "alpha")
        clear_aliases()
        assert list_aliases() == {}
