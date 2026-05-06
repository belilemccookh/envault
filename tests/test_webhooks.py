"""Tests for envault.webhooks."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.webhooks import (
    WebhookError,
    _webhooks_path,
    list_hooks,
    notify,
    register,
    unregister,
)


@pytest.fixture()
def tmp_storage(tmp_path: Path) -> Path:
    return tmp_path


class TestRegister:
    def test_adds_url(self, tmp_storage: Path) -> None:
        register("proj", "https://example.com/hook", tmp_storage)
        assert "https://example.com/hook" in list_hooks("proj", tmp_storage)

    def test_duplicate_not_added_twice(self, tmp_storage: Path) -> None:
        register("proj", "https://example.com/hook", tmp_storage)
        register("proj", "https://example.com/hook", tmp_storage)
        assert list_hooks("proj", tmp_storage).count("https://example.com/hook") == 1

    def test_invalid_scheme_raises(self, tmp_storage: Path) -> None:
        with pytest.raises(WebhookError, match="Invalid URL scheme"):
            register("proj", "ftp://bad.example.com", tmp_storage)

    def test_multiple_urls(self, tmp_storage: Path) -> None:
        register("proj", "https://a.example.com", tmp_storage)
        register("proj", "https://b.example.com", tmp_storage)
        hooks = list_hooks("proj", tmp_storage)
        assert len(hooks) == 2


class TestUnregister:
    def test_removes_url(self, tmp_storage: Path) -> None:
        register("proj", "https://example.com/hook", tmp_storage)
        removed = unregister("proj", "https://example.com/hook", tmp_storage)
        assert removed is True
        assert list_hooks("proj", tmp_storage) == []

    def test_returns_false_if_not_present(self, tmp_storage: Path) -> None:
        assert unregister("proj", "https://missing.example.com", tmp_storage) is False

    def test_project_key_removed_when_empty(self, tmp_storage: Path) -> None:
        register("proj", "https://example.com/hook", tmp_storage)
        unregister("proj", "https://example.com/hook", tmp_storage)
        raw = json.loads(_webhooks_path(tmp_storage).read_text())
        assert "proj" not in raw


class TestNotify:
    def _make_response(self, status: int = 200) -> MagicMock:
        resp = MagicMock()
        resp.status = status
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        return resp

    def test_returns_empty_when_no_hooks(self, tmp_storage: Path) -> None:
        results = notify("proj", "env.updated", base_dir=tmp_storage)
        assert results == []

    def test_successful_post(self, tmp_storage: Path) -> None:
        register("proj", "https://example.com/hook", tmp_storage)
        with patch("urllib.request.urlopen", return_value=self._make_response(200)):
            results = notify("proj", "env.updated", base_dir=tmp_storage)
        assert len(results) == 1
        url, ok, msg = results[0]
        assert ok is True
        assert msg == "200"

    def test_failed_post_captured(self, tmp_storage: Path) -> None:
        import urllib.error

        register("proj", "https://example.com/hook", tmp_storage)
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            results = notify("proj", "env.updated", base_dir=tmp_storage)
        _, ok, msg = results[0]
        assert ok is False
        assert "connection refused" in msg
