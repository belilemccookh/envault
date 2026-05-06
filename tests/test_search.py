"""Tests for envault.search."""
from __future__ import annotations

import pytest

from envault.search import SearchMatch, search_keys, search_values
from envault.storage import save_env

PASS = "hunter2"


@pytest.fixture()
def tmp_storage(tmp_path, monkeypatch):
    import envault.storage as st
    import envault.crypto as cr

    monkeypatch.setattr(st, "STORAGE_DIR", tmp_path / "store")
    monkeypatch.setattr(cr, "SALT_FILE", tmp_path / "salt")
    (tmp_path / "store").mkdir()
    return tmp_path


@pytest.fixture()
def seeded(tmp_storage):
    save_env("alpha", {"DATABASE_URL": "postgres://localhost", "SECRET_KEY": "abc"}, PASS)
    save_env("beta", {"DATABASE_URL": "mysql://remote", "API_TOKEN": "xyz"}, PASS)
    save_env("gamma", {"REDIS_URL": "redis://localhost", "DEBUG": "true"}, PASS)
    return tmp_storage


class TestSearchKeys:
    def test_finds_matching_key_across_projects(self, seeded):
        result = search_keys(PASS, "DATABASE")
        assert result.found
        projects = {m.project for m in result.matches}
        assert projects == {"alpha", "beta"}

    def test_case_insensitive_by_default(self, seeded):
        result = search_keys(PASS, "database_url")
        assert len(result.matches) == 2

    def test_case_sensitive_no_match(self, seeded):
        result = search_keys(PASS, "database_url", case_sensitive=True)
        assert not result.found

    def test_scoped_to_project(self, seeded):
        result = search_keys(PASS, "DATABASE", project="alpha")
        assert len(result.matches) == 1
        assert result.matches[0].project == "alpha"

    def test_no_match_returns_empty(self, seeded):
        result = search_keys(PASS, "NONEXISTENT")
        assert not result.found
        assert result.matches == []

    def test_by_project_groups_correctly(self, seeded):
        result = search_keys(PASS, "DATABASE")
        grouped = result.by_project()
        assert set(grouped.keys()) == {"alpha", "beta"}
        assert all(len(v) == 1 for v in grouped.values())


class TestSearchValues:
    def test_finds_localhost_in_multiple_projects(self, seeded):
        result = search_values(PASS, "localhost")
        assert result.found
        projects = {m.project for m in result.matches}
        assert "alpha" in projects
        assert "gamma" in projects

    def test_case_insensitive_value_search(self, seeded):
        result = search_values(PASS, "POSTGRES")
        assert result.found

    def test_case_sensitive_value_search(self, seeded):
        result = search_values(PASS, "POSTGRES", case_sensitive=True)
        assert not result.found

    def test_match_contains_correct_key_and_value(self, seeded):
        result = search_values(PASS, "xyz")
        assert len(result.matches) == 1
        m: SearchMatch = result.matches[0]
        assert m.project == "beta"
        assert m.key == "API_TOKEN"
        assert m.value == "xyz"

    def test_invalid_passphrase_skips_project(self, seeded):
        result = search_values("wrong-pass", "localhost")
        assert not result.found
