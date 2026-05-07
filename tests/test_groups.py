"""Unit tests for envault.groups."""

from __future__ import annotations

import pytest

from envault.groups import (
    GroupError,
    add_project,
    delete_group,
    get_group,
    list_groups,
    remove_project,
)


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.groups._base_dir", lambda: tmp_path)
    return tmp_path


class TestAddProject:
    def test_add_single(self):
        members = add_project("backend", "api")
        assert members == ["api"]

    def test_add_multiple(self):
        add_project("backend", "api")
        members = add_project("backend", "worker")
        assert members == ["api", "worker"]

    def test_add_idempotent(self):
        add_project("backend", "api")
        members = add_project("backend", "api")
        assert members.count("api") == 1

    def test_empty_group_raises(self):
        with pytest.raises(GroupError, match="Group name"):
            add_project("", "api")

    def test_empty_project_raises(self):
        with pytest.raises(GroupError, match="Project name"):
            add_project("backend", "")


class TestRemoveProject:
    def test_remove_existing(self):
        add_project("backend", "api")
        add_project("backend", "worker")
        members = remove_project("backend", "api")
        assert "api" not in members
        assert "worker" in members

    def test_remove_last_deletes_group(self):
        add_project("solo", "only")
        remove_project("solo", "only")
        assert "solo" not in list_groups()

    def test_remove_nonexistent_group_raises(self):
        with pytest.raises(GroupError, match="does not exist"):
            remove_project("ghost", "api")

    def test_remove_nonexistent_project_raises(self):
        add_project("backend", "api")
        with pytest.raises(GroupError, match="not in group"):
            remove_project("backend", "ghost")


class TestListAndGet:
    def test_list_empty(self):
        assert list_groups() == {}

    def test_list_returns_all(self):
        add_project("a", "p1")
        add_project("b", "p2")
        data = list_groups()
        assert set(data.keys()) == {"a", "b"}

    def test_get_existing(self):
        add_project("backend", "api")
        assert get_group("backend") == ["api"]

    def test_get_missing_raises(self):
        with pytest.raises(GroupError, match="does not exist"):
            get_group("missing")


class TestDeleteGroup:
    def test_delete_removes_group(self):
        add_project("temp", "svc")
        delete_group("temp")
        assert "temp" not in list_groups()

    def test_delete_missing_raises(self):
        with pytest.raises(GroupError, match="does not exist"):
            delete_group("nope")
