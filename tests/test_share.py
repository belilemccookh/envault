"""Tests for envault.share and envault.cli_share."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.share import ShareError, export_bundle, import_bundle
from envault.cli_share import share_export_cmd, share_import_cmd

MASTER = "master-pass"
SHARE = "share-pass"
PROJECT = "myapp"
ENV = {"DB_URL": "postgres://localhost/db", "SECRET": "s3cr3t"}


@pytest.fixture()
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    # Also patch storage module to use tmp_path
    import envault.storage as st
    monkeypatch.setattr(st, "_base_dir", lambda: tmp_path)
    return tmp_path


@pytest.fixture()
def stored_project(tmp_storage):
    from envault.storage import save_env
    save_env(PROJECT, ENV, MASTER)
    return PROJECT


class TestExportBundle:
    def test_creates_bundle_file(self, tmp_path, stored_project):
        out = tmp_path / "test.envbundle"
        result = export_bundle(PROJECT, MASTER, SHARE, out)
        assert result == out
        assert out.exists()

    def test_bundle_is_valid_json(self, tmp_path, stored_project):
        out = tmp_path / "test.envbundle"
        export_bundle(PROJECT, MASTER, SHARE, out)
        data = json.loads(out.read_text())
        assert data["project"] == PROJECT
        assert "data" in data

    def test_wrong_passphrase_raises(self, tmp_path, stored_project):
        out = tmp_path / "test.envbundle"
        with pytest.raises(ShareError, match="not found or wrong passphrase"):
            export_bundle(PROJECT, "bad-pass", SHARE, out)


class TestImportBundle:
    def test_roundtrip(self, tmp_path, stored_project):
        out = tmp_path / "test.envbundle"
        export_bundle(PROJECT, MASTER, SHARE, out)

        from envault.storage import load_env
        name = import_bundle(out, SHARE, MASTER, project_override="myapp2")
        assert name == "myapp2"
        assert load_env("myapp2", MASTER) == ENV

    def test_wrong_share_passphrase_raises(self, tmp_path, stored_project):
        out = tmp_path / "test.envbundle"
        export_bundle(PROJECT, MASTER, SHARE, out)
        with pytest.raises(ShareError, match="wrong share passphrase"):
            import_bundle(out, "wrong", MASTER)

    def test_invalid_bundle_raises(self, tmp_path):
        bad = tmp_path / "bad.envbundle"
        bad.write_text("not json")
        with pytest.raises(ShareError, match="Invalid bundle"):
            import_bundle(bad, SHARE, MASTER)


class TestCLIShare:
    @pytest.fixture()
    def runner(self):
        return CliRunner()

    def test_share_export_success(self, runner, tmp_path, stored_project):
        out = str(tmp_path / "out.envbundle")
        result = runner.invoke(
            share_export_cmd,
            [PROJECT, "--passphrase", MASTER, "--share-passphrase", SHARE, "--output", out],
        )
        assert result.exit_code == 0
        assert "Bundle written to" in result.output

    def test_share_import_success(self, runner, tmp_path, stored_project):
        out = tmp_path / "out.envbundle"
        export_bundle(PROJECT, MASTER, SHARE, out)
        result = runner.invoke(
            share_import_cmd,
            [str(out), "--share-passphrase", SHARE, "--passphrase", MASTER, "--project", "imported"],
        )
        assert result.exit_code == 0
        assert "imported" in result.output
