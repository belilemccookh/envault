"""Unit tests for envault.favorites."""
from __future__ import annotations

import pytest

from envault import favorites as fav_lib
from envault.favorites import FavoriteError


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    """Redirect storage root to a temporary directory."""
    import envault.storage as _storage
    monkeypatch.setattr(_storage, "BASE_DIR", tmp_path)
    yield tmp_path


class TestAddFavorite:
    def test_add_single(self):
        fav_lib.add_favorite("alpha")
        assert fav_lib.list_favorites() == ["alpha"]

    def test_add_multiple_preserves_order(self):
        for name in ["gamma", "beta", "alpha"]:
            fav_lib.add_favorite(name)
        assert fav_lib.list_favorites() == ["gamma", "beta", "alpha"]

    def test_add_idempotent(self):
        fav_lib.add_favorite("alpha")
        fav_lib.add_favorite("alpha")
        assert fav_lib.list_favorites().count("alpha") == 1

    def test_empty_name_raises(self):
        with pytest.raises(FavoriteError):
            fav_lib.add_favorite("")

    def test_whitespace_name_raises(self):
        with pytest.raises(FavoriteError):
            fav_lib.add_favorite("   ")


class TestRemoveFavorite:
    def test_remove_existing(self):
        fav_lib.add_favorite("alpha")
        fav_lib.remove_favorite("alpha")
        assert "alpha" not in fav_lib.list_favorites()

    def test_remove_nonexistent_raises(self):
        with pytest.raises(FavoriteError, match="not in favorites"):
            fav_lib.remove_favorite("ghost")

    def test_remove_does_not_affect_others(self):
        fav_lib.add_favorite("keep")
        fav_lib.add_favorite("drop")
        fav_lib.remove_favorite("drop")
        assert fav_lib.list_favorites() == ["keep"]


class TestIsFavorite:
    def test_true_when_added(self):
        fav_lib.add_favorite("proj")
        assert fav_lib.is_favorite("proj") is True

    def test_false_when_absent(self):
        assert fav_lib.is_favorite("missing") is False

    def test_false_after_removal(self):
        fav_lib.add_favorite("proj")
        fav_lib.remove_favorite("proj")
        assert fav_lib.is_favorite("proj") is False


class TestClearFavorites:
    def test_returns_count(self):
        fav_lib.add_favorite("a")
        fav_lib.add_favorite("b")
        assert fav_lib.clear_favorites() == 2

    def test_list_empty_after_clear(self):
        fav_lib.add_favorite("a")
        fav_lib.clear_favorites()
        assert fav_lib.list_favorites() == []

    def test_clear_empty_returns_zero(self):
        assert fav_lib.clear_favorites() == 0
