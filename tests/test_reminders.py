"""Tests for envault.reminders."""
from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

import envault.reminders as rem
from envault.reminders import (
    ReminderError,
    delete_reminder,
    due_reminders,
    get_reminder,
    list_reminders,
    set_reminder,
)


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.storage._base_dir", lambda: tmp_path)
    monkeypatch.setattr("envault.reminders._reminders_path", lambda: tmp_path / "reminders.json")
    yield tmp_path


class TestSetReminder:
    def test_creates_entry(self):
        entry = set_reminder("proj", 7)
        assert entry["project"] == "proj"
        assert "due" in entry

    def test_due_date_roughly_correct(self):
        entry = set_reminder("proj", 10)
        due = datetime.fromisoformat(entry["due"])
        expected = datetime.utcnow() + timedelta(days=10)
        assert abs((due - expected).total_seconds()) < 5

    def test_zero_days_raises(self):
        with pytest.raises(ReminderError):
            set_reminder("proj", 0)

    def test_negative_days_raises(self):
        with pytest.raises(ReminderError):
            set_reminder("proj", -3)

    def test_note_stored(self):
        entry = set_reminder("proj", 5, note="rotate soon")
        assert entry["note"] == "rotate soon"

    def test_overwrite_existing(self):
        set_reminder("proj", 5)
        entry = set_reminder("proj", 90)
        due = datetime.fromisoformat(entry["due"])
        assert (due - datetime.utcnow()).days >= 89


class TestGetAndDelete:
    def test_get_returns_none_when_missing(self):
        assert get_reminder("ghost") is None

    def test_get_returns_entry(self):
        set_reminder("myproj", 14)
        assert get_reminder("myproj") is not None

    def test_delete_existing(self):
        set_reminder("myproj", 14)
        assert delete_reminder("myproj") is True
        assert get_reminder("myproj") is None

    def test_delete_missing_returns_false(self):
        assert delete_reminder("nope") is False


class TestListAndDue:
    def test_list_empty(self):
        assert list_reminders() == []

    def test_list_sorted_by_due(self):
        set_reminder("b", 10)
        set_reminder("a", 2)
        names = [r["project"] for r in list_reminders()]
        assert names == ["a", "b"]

    def test_due_reminders_past(self):
        past = (datetime.utcnow() - timedelta(days=1)).isoformat(timespec="seconds")
        data = {"old": {"project": "old", "due": past, "note": "", "created": past}}
        (pytest.importorskip("pathlib").Path(rem._reminders_path())).write_text(
            __import__("json").dumps(data)
        )
        assert len(due_reminders()) == 1

    def test_future_reminder_not_due(self):
        set_reminder("future", 30)
        assert due_reminders() == []
