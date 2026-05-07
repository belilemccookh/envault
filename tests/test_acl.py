"""Tests for envault.acl and envault.cli_acl."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault import acl as acl_lib
from envault.cli_acl import acl_cmd


@pytest.fixture()
def tmp_storage(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# Library tests
# ---------------------------------------------------------------------------

class TestGrant:
    def test_grant_returns_acl(self, tmp_storage: Path) -> None:
        result = acl_lib.grant(tmp_storage, "proj", "alice", "editor")
        assert result == {"alice": "editor"}

    def test_grant_persists(self, tmp_storage: Path) -> None:
        acl_lib.grant(tmp_storage, "proj", "bob", "viewer")
        assert acl_lib.get_role(tmp_storage, "proj", "bob") == "viewer"

    def test_overwrite_role(self, tmp_storage: Path) -> None:
        acl_lib.grant(tmp_storage, "proj", "alice", "viewer")
        acl_lib.grant(tmp_storage, "proj", "alice", "owner")
        assert acl_lib.get_role(tmp_storage, "proj", "alice") == "owner"

    def test_empty_user_raises(self, tmp_storage: Path) -> None:
        with pytest.raises(acl_lib.ACLError, match="empty"):
            acl_lib.grant(tmp_storage, "proj", "  ", "viewer")

    def test_invalid_role_raises(self, tmp_storage: Path) -> None:
        with pytest.raises(acl_lib.ACLError, match="Invalid role"):
            acl_lib.grant(tmp_storage, "proj", "alice", "superuser")


class TestRevoke:
    def test_revoke_removes_user(self, tmp_storage: Path) -> None:
        acl_lib.grant(tmp_storage, "proj", "alice", "editor")
        acl_lib.revoke(tmp_storage, "proj", "alice")
        assert acl_lib.get_role(tmp_storage, "proj", "alice") is None

    def test_revoke_missing_user_raises(self, tmp_storage: Path) -> None:
        with pytest.raises(acl_lib.ACLError, match="not found"):
            acl_lib.revoke(tmp_storage, "proj", "ghost")


class TestCheckPermission:
    def test_owner_passes_all_roles(self, tmp_storage: Path) -> None:
        acl_lib.grant(tmp_storage, "proj", "alice", "owner")
        for role in acl_lib.ROLES:
            assert acl_lib.check_permission(tmp_storage, "proj", "alice", role)

    def test_viewer_fails_editor(self, tmp_storage: Path) -> None:
        acl_lib.grant(tmp_storage, "proj", "bob", "viewer")
        assert not acl_lib.check_permission(tmp_storage, "proj", "bob", "editor")

    def test_unknown_user_returns_false(self, tmp_storage: Path) -> None:
        assert not acl_lib.check_permission(tmp_storage, "proj", "nobody", "viewer")


class TestListAcl:
    def test_empty_project(self, tmp_storage: Path) -> None:
        assert acl_lib.list_acl(tmp_storage, "new") == []

    def test_sorted_by_user(self, tmp_storage: Path) -> None:
        acl_lib.grant(tmp_storage, "proj", "zara", "viewer")
        acl_lib.grant(tmp_storage, "proj", "alice", "owner")
        names = [e["user"] for e in acl_lib.list_acl(tmp_storage, "proj")]
        assert names == ["alice", "zara"]


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def _invoke(runner: CliRunner, tmp_storage: Path, *args: str):
    return runner.invoke(acl_cmd, args, obj={"storage_dir": tmp_storage})


def test_cli_grant_success(runner: CliRunner, tmp_storage: Path) -> None:
    result = _invoke(runner, tmp_storage, "grant", "proj", "alice", "editor")
    assert result.exit_code == 0
    assert "Granted" in result.output


def test_cli_list_shows_users(runner: CliRunner, tmp_storage: Path) -> None:
    acl_lib.grant(tmp_storage, "proj", "alice", "owner")
    result = _invoke(runner, tmp_storage, "list", "proj")
    assert "alice" in result.output
    assert "owner" in result.output


def test_cli_revoke_success(runner: CliRunner, tmp_storage: Path) -> None:
    acl_lib.grant(tmp_storage, "proj", "alice", "editor")
    result = _invoke(runner, tmp_storage, "revoke", "proj", "alice")
    assert result.exit_code == 0
    assert "Revoked" in result.output


def test_cli_check_allowed(runner: CliRunner, tmp_storage: Path) -> None:
    acl_lib.grant(tmp_storage, "proj", "alice", "editor")
    result = _invoke(runner, tmp_storage, "check", "proj", "alice", "viewer")
    assert result.exit_code == 0


def test_cli_check_denied_exits_1(runner: CliRunner, tmp_storage: Path) -> None:
    acl_lib.grant(tmp_storage, "proj", "alice", "viewer")
    result = _invoke(runner, tmp_storage, "check", "proj", "alice", "owner")
    assert result.exit_code != 0
