"""Unit tests for envault.pins."""

from __future__ import annotations

import pytest

from envault.pins import PinError, all_pins, get_pins, is_pinned, pin_key, unpin_key


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.storage._base_dir", lambda: tmp_path)
    monkeypatch.setattr("envault.pins._base_dir", lambda: tmp_path)


class TestPinKey:
    def test_pin_and_retrieve(self):
        pin_key("myapp", "SECRET_KEY")
        assert "SECRET_KEY" in get_pins("myapp")

    def test_pin_idempotent(self):
        pin_key("myapp", "SECRET_KEY")
        pin_key("myapp", "SECRET_KEY")
        assert get_pins("myapp").count("SECRET_KEY") == 1

    def test_multiple_keys(self):
        pin_key("myapp", "KEY_A")
        pin_key("myapp", "KEY_B")
        pins = get_pins("myapp")
        assert "KEY_A" in pins
        assert "KEY_B" in pins

    def test_empty_project_raises(self):
        with pytest.raises(PinError, match="project name"):
            pin_key("", "SOME_KEY")

    def test_empty_key_raises(self):
        with pytest.raises(PinError, match="key name"):
            pin_key("myapp", "")


class TestUnpinKey:
    def test_unpin_existing_returns_true(self):
        pin_key("myapp", "TOKEN")
        assert unpin_key("myapp", "TOKEN") is True
        assert "TOKEN" not in get_pins("myapp")

    def test_unpin_nonexistent_returns_false(self):
        assert unpin_key("myapp", "GHOST") is False

    def test_project_removed_when_empty(self):
        pin_key("myapp", "ONLY_KEY")
        unpin_key("myapp", "ONLY_KEY")
        assert "myapp" not in all_pins()


class TestIsPinned:
    def test_true_when_pinned(self):
        pin_key("proj", "DB_PASS")
        assert is_pinned("proj", "DB_PASS") is True

    def test_false_when_not_pinned(self):
        assert is_pinned("proj", "MISSING") is False


class TestAllPins:
    def test_returns_all_projects(self):
        pin_key("alpha", "K1")
        pin_key("beta", "K2")
        data = all_pins()
        assert "alpha" in data
        assert "beta" in data

    def test_empty_when_no_pins(self):
        assert all_pins() == {}
