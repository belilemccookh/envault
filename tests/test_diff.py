"""Tests for envault.diff module."""
from __future__ import annotations

import pytest

from envault.diff import DiffResult, diff_envs, format_diff


OLD = {"FOO": "1", "BAR": "old", "KEEP": "same"}
NEW = {"BAR": "new", "KEEP": "same", "BAZ": "added"}


class TestDiffEnvs:
    def test_added_keys(self):
        result = diff_envs(OLD, NEW)
        assert "BAZ" in result.added
        assert result.added["BAZ"] == "added"

    def test_removed_keys(self):
        result = diff_envs(OLD, NEW)
        assert "FOO" in result.removed
        assert result.removed["FOO"] == "1"

    def test_changed_keys(self):
        result = diff_envs(OLD, NEW)
        assert "BAR" in result.changed
        assert result.changed["BAR"] == ("old", "new")

    def test_unchanged_keys(self):
        result = diff_envs(OLD, NEW)
        assert "KEEP" in result.unchanged

    def test_no_changes(self):
        result = diff_envs(OLD, OLD)
        assert not result.has_changes

    def test_has_changes(self):
        result = diff_envs(OLD, NEW)
        assert result.has_changes

    def test_empty_dicts(self):
        result = diff_envs({}, {})
        assert not result.has_changes

    def test_all_added(self):
        result = diff_envs({}, {"X": "1"})
        assert result.added == {"X": "1"}
        assert not result.removed


class TestDiffResultSummary:
    def test_summary_no_changes(self):
        r = DiffResult()
        assert r.summary == "No changes."

    def test_summary_with_changes(self):
        result = diff_envs(OLD, NEW)
        summary = result.summary
        assert "+1 added" in summary
        assert "-1 removed" in summary
        assert "~1 changed" in summary


class TestFormatDiff:
    def test_masks_values_by_default(self):
        result = diff_envs(OLD, NEW)
        lines = format_diff(result)
        for line in lines:
            assert "***" in line

    def test_shows_values_when_requested(self):
        result = diff_envs(OLD, NEW)
        lines = format_diff(result, mask_values=False)
        joined = "\n".join(lines)
        assert "added" in joined
        assert "old" in joined
        assert "new" in joined

    def test_prefix_symbols(self):
        result = diff_envs(OLD, NEW)
        lines = format_diff(result)
        prefixes = {line[0] for line in lines}
        assert prefixes <= {"+", "-", "~"}

    def test_empty_diff_returns_empty_list(self):
        result = diff_envs(OLD, OLD)
        assert format_diff(result) == []
