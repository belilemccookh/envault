"""Tests for envault.templates and envault.cli_templates."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envault.templates import (
    TemplateError,
    apply_template,
    delete_template,
    list_templates,
    load_template,
    save_template,
)
from envault.cli_templates import templates_cmd


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.templates._base_dir", lambda: tmp_path)
    monkeypatch.setattr("envault.storage._base_dir", lambda: tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


# ── unit tests ──────────────────────────────────────────────────────────────

class TestSaveAndLoad:
    def test_roundtrip(self):
        save_template("web", {"HOST": "localhost", "PORT": "8080"})
        keys = load_template("web")
        assert keys == {"HOST": "localhost", "PORT": "8080"}

    def test_empty_name_raises(self):
        with pytest.raises(TemplateError, match="empty"):
            save_template("", {})

    def test_missing_template_raises(self):
        with pytest.raises(TemplateError, match="not found"):
            load_template("nonexistent")


class TestListAndDelete:
    def test_list_empty(self):
        assert list_templates() == []

    def test_list_returns_metadata(self):
        save_template("alpha", {}, description="first")
        save_template("beta", {"X": "1"})
        names = [t["name"] for t in list_templates()]
        assert names == ["alpha", "beta"]

    def test_delete_removes_template(self):
        save_template("tmp", {"A": "1"})
        delete_template("tmp")
        assert not any(t["name"] == "tmp" for t in list_templates())

    def test_delete_missing_raises(self):
        with pytest.raises(TemplateError):
            delete_template("ghost")


class TestApplyTemplate:
    def test_apply_uses_defaults(self):
        save_template("base", {"DB": "sqlite", "PORT": "5432"})
        env = apply_template("base")
        assert env == {"DB": "sqlite", "PORT": "5432"}

    def test_apply_overrides_take_precedence(self):
        save_template("base", {"DB": "sqlite", "PORT": "5432"})
        env = apply_template("base", overrides={"PORT": "9999"})
        assert env["PORT"] == "9999"
        assert env["DB"] == "sqlite"


# ── CLI tests ────────────────────────────────────────────────────────────────

class TestCLITemplates:
    def test_list_empty(self, runner):
        result = runner.invoke(templates_cmd, ["list"])
        assert result.exit_code == 0
        assert "No templates" in result.output

    def test_save_and_show(self, runner):
        save_template("demo", {"KEY": "val"})
        result = runner.invoke(templates_cmd, ["show", "demo"])
        assert result.exit_code == 0
        assert "KEY=val" in result.output

    def test_show_missing(self, runner):
        result = runner.invoke(templates_cmd, ["show", "nope"])
        assert result.exit_code != 0

    def test_delete_cmd(self, runner):
        save_template("gone", {})
        result = runner.invoke(templates_cmd, ["delete", "gone"], input="y\n")
        assert result.exit_code == 0
        assert list_templates() == []
