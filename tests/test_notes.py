"""Tests for envault.notes and envault.cli_notes."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault import notes as notes_lib
from envault.cli_notes import notes_cmd


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    """Redirect storage to a temp directory for every test."""
    import envault.storage as storage_mod
    import envault.notes as notes_mod

    monkeypatch.setattr(storage_mod, "STORAGE_DIR", tmp_path)
    monkeypatch.setattr(notes_mod, "_project_path",
                        lambda p: tmp_path / p)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


# ---------------------------------------------------------------------------
# Library tests
# ---------------------------------------------------------------------------

class TestAddNote:
    def test_returns_entry_with_id(self):
        entry = notes_lib.add_note("myproject", "hello world")
        assert entry["id"] == 1
        assert entry["text"] == "hello world"
        assert "ts" in entry

    def test_sequential_ids(self):
        notes_lib.add_note("p", "first")
        entry = notes_lib.add_note("p", "second")
        assert entry["id"] == 2

    def test_empty_text_raises(self):
        with pytest.raises(ValueError, match="empty"):
            notes_lib.add_note("p", "   ")

    def test_strips_whitespace(self):
        entry = notes_lib.add_note("p", "  trimmed  ")
        assert entry["text"] == "trimmed"


class TestListNotes:
    def test_empty_project_returns_empty_list(self):
        assert notes_lib.list_notes("ghost") == []

    def test_returns_all_notes(self):
        notes_lib.add_note("p", "a")
        notes_lib.add_note("p", "b")
        assert len(notes_lib.list_notes("p")) == 2


class TestDeleteNote:
    def test_delete_existing_returns_true(self):
        notes_lib.add_note("p", "to delete")
        assert notes_lib.delete_note("p", 1) is True
        assert notes_lib.list_notes("p") == []

    def test_delete_missing_returns_false(self):
        assert notes_lib.delete_note("p", 99) is False


class TestClearNotes:
    def test_returns_count(self):
        notes_lib.add_note("p", "x")
        notes_lib.add_note("p", "y")
        assert notes_lib.clear_notes("p") == 2

    def test_clears_all(self):
        notes_lib.add_note("p", "x")
        notes_lib.clear_notes("p")
        assert notes_lib.list_notes("p") == []


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_cli_add_note(runner):
    result = runner.invoke(notes_cmd, ["add", "proj", "my note"])
    assert result.exit_code == 0
    assert "Note #1 added" in result.output


def test_cli_list_notes(runner):
    notes_lib.add_note("proj", "alpha")
    notes_lib.add_note("proj", "beta")
    result = runner.invoke(notes_cmd, ["list", "proj"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_cli_list_empty(runner):
    result = runner.invoke(notes_cmd, ["list", "nobody"])
    assert result.exit_code == 0
    assert "No notes" in result.output


def test_cli_delete_note(runner):
    notes_lib.add_note("proj", "bye")
    result = runner.invoke(notes_cmd, ["delete", "proj", "1"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_cli_delete_missing_note(runner):
    result = runner.invoke(notes_cmd, ["delete", "proj", "42"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_cli_show_note(runner):
    notes_lib.add_note("proj", "show me")
    result = runner.invoke(notes_cmd, ["show", "proj", "1"])
    assert result.exit_code == 0
    assert "show me" in result.output
