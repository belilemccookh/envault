"""Tests for envault crypto and storage modules."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from envault.crypto import encrypt, decrypt, derive_key
from envault import storage


PASSPHRASE = "super-secret-passphrase"
SAMPLE_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n"


@pytest.fixture(autouse=True)
def patch_salt(tmp_path, monkeypatch):
    """Redirect salt and store files to a temp directory."""
    salt_file = tmp_path / "salt"
    store_dir = tmp_path / "store"
    monkeypatch.setattr("envault.crypto.SALT_FILE", salt_file)
    monkeypatch.setattr("envault.crypto.KEY_FILE", tmp_path / "master.key")
    monkeypatch.setattr("envault.storage.STORE_DIR", store_dir)


class TestCrypto:
    def test_encrypt_returns_bytes(self):
        token = encrypt(SAMPLE_ENV, PASSPHRASE)
        assert isinstance(token, bytes)

    def test_decrypt_roundtrip(self):
        token = encrypt(SAMPLE_ENV, PASSPHRASE)
        result = decrypt(token, PASSPHRASE)
        assert result == SAMPLE_ENV

    def test_wrong_passphrase_raises(self):
        token = encrypt(SAMPLE_ENV, PASSPHRASE)
        with pytest.raises(Exception):
            decrypt(token, "wrong-passphrase")

    def test_derive_key_deterministic(self):
        key1 = derive_key(PASSPHRASE)
        key2 = derive_key(PASSPHRASE)
        assert key1 == key2

    def test_encrypt_produces_unique_tokens(self):
        """Each encrypt call should produce a different ciphertext (due to random IV/nonce)."""
        token1 = encrypt(SAMPLE_ENV, PASSPHRASE)
        token2 = encrypt(SAMPLE_ENV, PASSPHRASE)
        assert token1 != token2


class TestStorage:
    def test_save_and_load(self):
        storage.save_env("myproject", SAMPLE_ENV, PASSPHRASE)
        loaded = storage.load_env("myproject", PASSPHRASE)
        assert loaded == SAMPLE_ENV

    def test_load_missing_project_raises(self):
        with pytest.raises(FileNotFoundError):
            storage.load_env("nonexistent", PASSPHRASE)

    def test_list_projects(self):
        storage.save_env("alpha", SAMPLE_ENV, PASSPHRASE)
        storage.save_env("beta", SAMPLE_ENV, PASSPHRASE)
        projects = storage.list_projects()
        assert set(projects) == {"alpha", "beta"}

    def test_list_projects_empty(self):
        """list_projects should return an empty list when no projects have been saved."""
        projects = storage.list_projects()
        assert projects == []

    def test_delete_env(self):
        storage.save_env("todelete", SAMPLE_ENV, PASSPHRASE)
        assert storage.delete_env("todelete") is True
        assert storage.delete_env("todelete") is False
