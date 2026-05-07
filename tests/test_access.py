"""Tests for envault.access."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.access import (
    AccessError,
    set_permission,
    get_permission,
    check_read,
    check_write,
    list_permissions,
    remove_permission,
)


@pytest.fixture()
def tmp_storage(tmp_path: Path) -> Path:
    return tmp_path


class TestSetPermission:
    def test_returns_permission_dict(self, tmp_storage):
        result = set_permission(tmp_storage, "alpha", can_read=True, can_write=False)
        assert result == {"read": True, "write": False}

    def test_persists_to_disk(self, tmp_storage):
        set_permission(tmp_storage, "beta", can_read=False, can_write=True)
        perms = get_permission(tmp_storage, "beta")
        assert perms["read"] is False
        assert perms["write"] is True

    def test_overwrite_existing(self, tmp_storage):
        set_permission(tmp_storage, "gamma", can_read=True, can_write=True)
        set_permission(tmp_storage, "gamma", can_read=False, can_write=False)
        perms = get_permission(tmp_storage, "gamma")
        assert perms == {"read": False, "write": False}

    def test_empty_project_raises(self, tmp_storage):
        with pytest.raises(AccessError, match="empty"):
            set_permission(tmp_storage, "")


class TestGetPermission:
    def test_defaults_to_full_access_for_unknown_project(self, tmp_storage):
        perms = get_permission(tmp_storage, "unknown")
        assert perms == {"read": True, "write": True}

    def test_returns_stored_value(self, tmp_storage):
        set_permission(tmp_storage, "delta", can_read=True, can_write=False)
        assert get_permission(tmp_storage, "delta")["write"] is False


class TestCheckReadWrite:
    def test_check_read_passes_when_allowed(self, tmp_storage):
        set_permission(tmp_storage, "proj", can_read=True, can_write=True)
        check_read(tmp_storage, "proj")  # should not raise

    def test_check_read_raises_when_denied(self, tmp_storage):
        set_permission(tmp_storage, "proj", can_read=False, can_write=True)
        with pytest.raises(AccessError, match="Read access denied"):
            check_read(tmp_storage, "proj")

    def test_check_write_passes_when_allowed(self, tmp_storage):
        set_permission(tmp_storage, "proj2", can_read=True, can_write=True)
        check_write(tmp_storage, "proj2")  # should not raise

    def test_check_write_raises_when_denied(self, tmp_storage):
        set_permission(tmp_storage, "proj2", can_read=True, can_write=False)
        with pytest.raises(AccessError, match="Write access denied"):
            check_write(tmp_storage, "proj2")

    def test_unknown_project_passes_both_checks(self, tmp_storage):
        check_read(tmp_storage, "ghost")
        check_write(tmp_storage, "ghost")


class TestListAndRemove:
    def test_list_empty_when_no_entries(self, tmp_storage):
        assert list_permissions(tmp_storage) == []

    def test_list_returns_sorted_entries(self, tmp_storage):
        set_permission(tmp_storage, "z_proj", can_read=True, can_write=True)
        set_permission(tmp_storage, "a_proj", can_read=False, can_write=True)
        result = list_permissions(tmp_storage)
        assert result[0]["project"] == "a_proj"
        assert result[1]["project"] == "z_proj"

    def test_remove_existing_returns_true(self, tmp_storage):
        set_permission(tmp_storage, "to_remove")
        assert remove_permission(tmp_storage, "to_remove") is True
        assert get_permission(tmp_storage, "to_remove") == {"read": True, "write": True}

    def test_remove_nonexistent_returns_false(self, tmp_storage):
        assert remove_permission(tmp_storage, "no_such") is False
