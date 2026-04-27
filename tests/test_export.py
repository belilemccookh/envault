"""Tests for envault export/import functionality."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_export import dump_cmd, export_cmd, import_cmd
from envault.export import dotenv_to_dict, env_to_dotenv, export_env, import_env


PASSPHRASE = "test-secret-passphrase"
PROJECT = "myapp"
ENV_VARS = {"DB_HOST": "localhost", "API_KEY": "abc123", "DEBUG": "true"}


@pytest.fixture
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    # Patch salt so key derivation is deterministic
    salt = b"\x00" * 16
    with patch("envault.crypto._get_or_create_salt", return_value=salt):
        yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


# --- Unit tests for export helpers ---

class TestDotenvHelpers:
    def test_env_to_dotenv_sorted(self):
        result = env_to_dotenv({"B": "2", "A": "1"})
        assert result.startswith('A="1"')

    def test_env_to_dotenv_escapes_quotes(self):
        result = env_to_dotenv({"MSG": 'say "hi"'})
        assert 'say \\"hi\\"' in result

    def test_dotenv_to_dict_basic(self):
        content = 'KEY=value\nFOO="bar"\n# comment\nEMPTY=\n'
        result = dotenv_to_dict(content)
        assert result["KEY"] == "value"
        assert result["FOO"] == "bar"
        assert "EMPTY" in result
        assert "comment" not in result

    def test_dotenv_roundtrip(self):
        original = {"X": "hello", "Y": "world"}
        assert dotenv_to_dict(env_to_dotenv(original)) == original


# --- Integration tests for export/import ---

class TestExportImport:
    def test_export_creates_file(self, tmp_storage):
        from envault.storage import save_env
        save_env(PROJECT, ENV_VARS, PASSPHRASE)

        bundle = str(tmp_storage / "bundle.evault")
        export_env(PROJECT, PASSPHRASE, bundle)
        assert Path(bundle).exists()
        assert Path(bundle).stat().st_size > 0

    def test_import_roundtrip(self, tmp_storage):
        from envault.storage import load_env, save_env
        save_env(PROJECT, ENV_VARS, PASSPHRASE)

        bundle = str(tmp_storage / "bundle.evault")
        export_env(PROJECT, PASSPHRASE, bundle)

        imported = import_env(bundle, PASSPHRASE, project_override="myapp2")
        assert imported == "myapp2"
        assert load_env("myapp2", PASSPHRASE) == ENV_VARS

    def test_import_wrong_passphrase_raises(self, tmp_storage):
        from envault.storage import save_env
        save_env(PROJECT, ENV_VARS, PASSPHRASE)
        bundle = str(tmp_storage / "bundle.evault")
        export_env(PROJECT, PASSPHRASE, bundle)

        with pytest.raises(ValueError, match="wrong passphrase"):
            import_env(bundle, "wrong-passphrase")

    def test_import_no_overwrite_raises(self, tmp_storage):
        from envault.storage import save_env
        save_env(PROJECT, ENV_VARS, PASSPHRASE)
        bundle = str(tmp_storage / "bundle.evault")
        export_env(PROJECT, PASSPHRASE, bundle)

        with pytest.raises(FileExistsError):
            import_env(bundle, PASSPHRASE)  # same project, overwrite=False

    def test_export_missing_project_raises(self, tmp_storage):
        with pytest.raises(KeyError):
            export_env("nonexistent", PASSPHRASE, str(tmp_storage / "x.evault"))
