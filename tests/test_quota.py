"""Tests for envault.quota."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.quota import (
    QuotaError,
    DEFAULT_MAX_KEYS,
    set_quota,
    get_quota,
    remove_quota,
    check_quota,
    list_quotas,
)


@pytest.fixture()
def tmp_storage(tmp_path: Path) -> Path:
    return tmp_path


class TestSetQuota:
    def test_returns_entry(self, tmp_storage):
        entry = set_quota(tmp_storage, "alpha", 50)
        assert entry == {"max_keys": 50}

    def test_persists_to_disk(self, tmp_storage):
        set_quota(tmp_storage, "alpha", 50)
        assert get_quota(tmp_storage, "alpha") == 50

    def test_overwrite_existing(self, tmp_storage):
        set_quota(tmp_storage, "alpha", 50)
        set_quota(tmp_storage, "alpha", 75)
        assert get_quota(tmp_storage, "alpha") == 75

    def test_empty_project_raises(self, tmp_storage):
        with pytest.raises(QuotaError, match="empty"):
            set_quota(tmp_storage, "", 10)

    def test_zero_max_keys_raises(self, tmp_storage):
        with pytest.raises(QuotaError, match="at least 1"):
            set_quota(tmp_storage, "alpha", 0)

    def test_negative_max_keys_raises(self, tmp_storage):
        with pytest.raises(QuotaError, match="at least 1"):
            set_quota(tmp_storage, "alpha", -5)


class TestGetQuota:
    def test_returns_default_when_not_set(self, tmp_storage):
        assert get_quota(tmp_storage, "unknown") == DEFAULT_MAX_KEYS

    def test_returns_set_value(self, tmp_storage):
        set_quota(tmp_storage, "beta", 20)
        assert get_quota(tmp_storage, "beta") == 20

    def test_empty_project_raises(self, tmp_storage):
        with pytest.raises(QuotaError):
            get_quota(tmp_storage, "")


class TestRemoveQuota:
    def test_removes_existing(self, tmp_storage):
        set_quota(tmp_storage, "gamma", 30)
        result = remove_quota(tmp_storage, "gamma")
        assert result is True
        assert get_quota(tmp_storage, "gamma") == DEFAULT_MAX_KEYS

    def test_returns_false_when_not_found(self, tmp_storage):
        assert remove_quota(tmp_storage, "nonexistent") is False

    def test_empty_project_raises(self, tmp_storage):
        with pytest.raises(QuotaError):
            remove_quota(tmp_storage, "")


class TestCheckQuota:
    def test_passes_when_under_limit(self, tmp_storage):
        set_quota(tmp_storage, "delta", 10)
        check_quota(tmp_storage, "delta", 9)  # should not raise

    def test_raises_when_at_limit(self, tmp_storage):
        set_quota(tmp_storage, "delta", 10)
        with pytest.raises(QuotaError, match="quota"):
            check_quota(tmp_storage, "delta", 10)

    def test_raises_when_over_limit(self, tmp_storage):
        set_quota(tmp_storage, "delta", 5)
        with pytest.raises(QuotaError, match="delta"):
            check_quota(tmp_storage, "delta", 99)

    def test_uses_default_when_no_quota_set(self, tmp_storage):
        # Should not raise for count well below default
        check_quota(tmp_storage, "epsilon", DEFAULT_MAX_KEYS - 1)


class TestListQuotas:
    def test_empty_when_none_set(self, tmp_storage):
        assert list_quotas(tmp_storage) == {}

    def test_lists_all_projects(self, tmp_storage):
        set_quota(tmp_storage, "a", 10)
        set_quota(tmp_storage, "b", 20)
        result = list_quotas(tmp_storage)
        assert result == {"a": 10, "b": 20}

    def test_excludes_removed_project(self, tmp_storage):
        set_quota(tmp_storage, "a", 10)
        set_quota(tmp_storage, "b", 20)
        remove_quota(tmp_storage, "a")
        assert list_quotas(tmp_storage) == {"b": 20}
