"""Tests for envault.expiry."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from envault.expiry import (
    ExpiryError,
    get_expiry,
    is_expired,
    list_expiries,
    remove_expiry,
    set_expiry,
)


@pytest.fixture()
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.expiry.BASE_DIR", tmp_path)
    return tmp_path


class TestSetExpiry:
    def test_returns_entry(self, tmp_storage):
        entry = set_expiry("myapp", 7, base_dir=tmp_storage)
        assert "expires_at" in entry
        assert "set_at" in entry

    def test_persists_to_disk(self, tmp_storage):
        set_expiry("myapp", 3, base_dir=tmp_storage)
        data = list_expiries(base_dir=tmp_storage)
        assert "myapp" in data

    def test_empty_project_raises(self, tmp_storage):
        with pytest.raises(ExpiryError, match="empty"):
            set_expiry("", 5, base_dir=tmp_storage)

    def test_zero_days_raises(self, tmp_storage):
        with pytest.raises(ExpiryError, match="positive"):
            set_expiry("myapp", 0, base_dir=tmp_storage)

    def test_negative_days_raises(self, tmp_storage):
        with pytest.raises(ExpiryError):
            set_expiry("myapp", -1, base_dir=tmp_storage)

    def test_overwrite_existing(self, tmp_storage):
        set_expiry("myapp", 1, base_dir=tmp_storage)
        entry = set_expiry("myapp", 30, base_dir=tmp_storage)
        expires = datetime.fromisoformat(entry["expires_at"])
        delta = expires - datetime.now(timezone.utc)
        assert delta.days >= 29


class TestGetExpiry:
    def test_returns_none_when_not_set(self, tmp_storage):
        assert get_expiry("ghost", base_dir=tmp_storage) is None

    def test_returns_entry_when_set(self, tmp_storage):
        set_expiry("myapp", 10, base_dir=tmp_storage)
        entry = get_expiry("myapp", base_dir=tmp_storage)
        assert entry is not None
        assert "expires_at" in entry


class TestRemoveExpiry:
    def test_removes_existing(self, tmp_storage):
        set_expiry("myapp", 5, base_dir=tmp_storage)
        assert remove_expiry("myapp", base_dir=tmp_storage) is True
        assert get_expiry("myapp", base_dir=tmp_storage) is None

    def test_returns_false_when_missing(self, tmp_storage):
        assert remove_expiry("ghost", base_dir=tmp_storage) is False


class TestIsExpired:
    def test_not_expired_for_future_date(self, tmp_storage):
        set_expiry("myapp", 30, base_dir=tmp_storage)
        assert is_expired("myapp", base_dir=tmp_storage) is False

    def test_expired_for_past_date(self, tmp_storage):
        import json
        from envault.expiry import _expiry_path, _now_iso

        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        path = _expiry_path(tmp_storage)
        path.write_text(json.dumps({"myapp": {"expires_at": past, "set_at": _now_iso()}}))
        assert is_expired("myapp", base_dir=tmp_storage) is True

    def test_no_expiry_returns_false(self, tmp_storage):
        assert is_expired("unset", base_dir=tmp_storage) is False


class TestListExpiries:
    def test_empty_when_none_set(self, tmp_storage):
        assert list_expiries(base_dir=tmp_storage) == {}

    def test_lists_all_entries(self, tmp_storage):
        set_expiry("alpha", 1, base_dir=tmp_storage)
        set_expiry("beta", 2, base_dir=tmp_storage)
        data = list_expiries(base_dir=tmp_storage)
        assert set(data.keys()) == {"alpha", "beta"}
