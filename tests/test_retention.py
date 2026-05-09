"""Tests for envault.retention."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.retention import (
    RetentionError,
    delete_policy,
    get_policy,
    list_policies,
    set_policy,
    _DEFAULT_MAX_HISTORY,
    _DEFAULT_MAX_SNAPSHOTS,
)


@pytest.fixture()
def tmp_storage(tmp_path: Path) -> Path:
    return tmp_path


# ---------------------------------------------------------------------------
# set_policy
# ---------------------------------------------------------------------------

class TestSetPolicy:
    def test_returns_policy_dict(self, tmp_storage):
        result = set_policy("proj", tmp_storage, max_snapshots=5, max_history=20)
        assert result == {"max_snapshots": 5, "max_history": 20}

    def test_persists_to_disk(self, tmp_storage):
        set_policy("proj", tmp_storage, max_snapshots=3)
        loaded = list_policies(tmp_storage)
        assert loaded["proj"]["max_snapshots"] == 3

    def test_partial_update_preserves_other_field(self, tmp_storage):
        set_policy("proj", tmp_storage, max_snapshots=5, max_history=30)
        set_policy("proj", tmp_storage, max_snapshots=8)
        policy = get_policy("proj", tmp_storage)
        assert policy["max_snapshots"] == 8
        assert policy["max_history"] == 30

    def test_empty_project_raises(self, tmp_storage):
        with pytest.raises(RetentionError):
            set_policy("", tmp_storage, max_snapshots=5)

    def test_zero_max_snapshots_raises(self, tmp_storage):
        with pytest.raises(RetentionError):
            set_policy("proj", tmp_storage, max_snapshots=0)

    def test_zero_max_history_raises(self, tmp_storage):
        with pytest.raises(RetentionError):
            set_policy("proj", tmp_storage, max_history=0)

    def test_multiple_projects_isolated(self, tmp_storage):
        set_policy("alpha", tmp_storage, max_snapshots=2)
        set_policy("beta", tmp_storage, max_snapshots=7)
        assert get_policy("alpha", tmp_storage)["max_snapshots"] == 2
        assert get_policy("beta", tmp_storage)["max_snapshots"] == 7


# ---------------------------------------------------------------------------
# get_policy
# ---------------------------------------------------------------------------

class TestGetPolicy:
    def test_defaults_when_no_policy_set(self, tmp_storage):
        policy = get_policy("unknown", tmp_storage)
        assert policy["max_snapshots"] == _DEFAULT_MAX_SNAPSHOTS
        assert policy["max_history"] == _DEFAULT_MAX_HISTORY

    def test_empty_project_raises(self, tmp_storage):
        with pytest.raises(RetentionError):
            get_policy("", tmp_storage)


# ---------------------------------------------------------------------------
# delete_policy
# ---------------------------------------------------------------------------

class TestDeletePolicy:
    def test_returns_true_when_deleted(self, tmp_storage):
        set_policy("proj", tmp_storage, max_snapshots=5)
        assert delete_policy("proj", tmp_storage) is True

    def test_returns_false_when_not_found(self, tmp_storage):
        assert delete_policy("ghost", tmp_storage) is False

    def test_policy_gone_after_delete(self, tmp_storage):
        set_policy("proj", tmp_storage, max_snapshots=5)
        delete_policy("proj", tmp_storage)
        policy = get_policy("proj", tmp_storage)
        assert policy["max_snapshots"] == _DEFAULT_MAX_SNAPSHOTS


# ---------------------------------------------------------------------------
# list_policies
# ---------------------------------------------------------------------------

def test_list_empty_storage(tmp_storage):
    assert list_policies(tmp_storage) == {}


def test_list_returns_all_projects(tmp_storage):
    set_policy("a", tmp_storage, max_snapshots=1)
    set_policy("b", tmp_storage, max_history=5)
    result = list_policies(tmp_storage)
    assert set(result.keys()) == {"a", "b"}
