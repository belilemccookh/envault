"""Unit tests for envault.snapshots."""
from __future__ import annotations

import pytest

from envault.snapshots import (
    SnapshotError,
    create_snapshot,
    delete_snapshot,
    get_snapshot,
    list_snapshots,
)


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    """Redirect storage to a temporary directory."""
    import envault.storage as st
    monkeypatch.setattr(st, "STORAGE_DIR", tmp_path)
    return tmp_path


ENV = {"API_KEY": "abc", "DEBUG": "true"}


class TestCreateSnapshot:
    def test_returns_entry(self):
        entry = create_snapshot("myapp", "v1", ENV)
        assert entry["label"] == "v1"
        assert entry["env"] == ENV
        assert entry["id"] == 1

    def test_sequential_ids(self):
        e1 = create_snapshot("myapp", "v1", ENV)
        e2 = create_snapshot("myapp", "v2", ENV)
        assert e2["id"] == e1["id"] + 1

    def test_empty_label_raises(self):
        with pytest.raises(SnapshotError, match="label"):
            create_snapshot("myapp", "  ", ENV)

    def test_created_at_present(self):
        entry = create_snapshot("myapp", "snap", ENV)
        assert "created_at" in entry
        assert entry["created_at"].endswith("+00:00")


class TestListSnapshots:
    def test_empty_list(self):
        assert list_snapshots("myapp") == []

    def test_multiple_entries(self):
        create_snapshot("myapp", "v1", ENV)
        create_snapshot("myapp", "v2", ENV)
        entries = list_snapshots("myapp")
        assert len(entries) == 2
        assert entries[0]["label"] == "v1"


class TestGetSnapshot:
    def test_retrieves_correct_entry(self):
        create_snapshot("myapp", "v1", {"X": "1"})
        create_snapshot("myapp", "v2", {"X": "2"})
        entry = get_snapshot("myapp", 2)
        assert entry["label"] == "v2"
        assert entry["env"] == {"X": "2"}

    def test_missing_id_raises(self):
        with pytest.raises(SnapshotError, match="not found"):
            get_snapshot("myapp", 99)


class TestDeleteSnapshot:
    def test_removes_entry(self):
        create_snapshot("myapp", "v1", ENV)
        create_snapshot("myapp", "v2", ENV)
        delete_snapshot("myapp", 1)
        remaining = list_snapshots("myapp")
        assert len(remaining) == 1
        assert remaining[0]["label"] == "v2"

    def test_missing_id_raises(self):
        with pytest.raises(SnapshotError, match="not found"):
            delete_snapshot("myapp", 42)
