"""CLI commands for managing project ACLs in envault."""

from __future__ import annotations

import click

from envault import acl as acl_lib
from envault.storage import _project_path  # reuse storage dir logic


def _storage(ctx: click.Context) -> object:
    return ctx.obj["storage_dir"]


@click.group("acl")
def acl_cmd() -> None:
    """Manage role-based access control for a project."""


@acl_cmd.command("grant")
@click.argument("project")
@click.argument("user")
@click.argument("role", type=click.Choice(acl_lib.ROLES))
@click.pass_context
def grant_cmd(ctx: click.Context, project: str, user: str, role: str) -> None:
    """Grant USER the ROLE on PROJECT."""
    storage_dir = _storage(ctx)
    try:
        acl_lib.grant(storage_dir, project, user, role)
        click.echo(f"Granted '{role}' to '{user}' on project '{project}'.")
    except acl_lib.ACLError as exc:
        raise click.ClickException(str(exc)) from exc


@acl_cmd.command("revoke")
@click.argument("project")
@click.argument("user")
@click.pass_context
def revoke_cmd(ctx: click.Context, project: str, user: str) -> None:
    """Revoke USER's access to PROJECT."""
    storage_dir = _storage(ctx)
    try:
        acl_lib.revoke(storage_dir, project, user)
        click.echo(f"Revoked access for '{user}' on project '{project}'.")
    except acl_lib.ACLError as exc:
        raise click.ClickException(str(exc)) from exc


@acl_cmd.command("list")
@click.argument("project")
@click.pass_context
def list_cmd(ctx: click.Context, project: str) -> None:
    """List all users and their roles for PROJECT."""
    storage_dir = _storage(ctx)
    entries = acl_lib.list_acl(storage_dir, project)
    if not entries:
        click.echo(f"No ACL entries for project '{project}'.")
        return
    for entry in entries:
        click.echo(f"  {entry['user']:30s}  {entry['role']}")


@acl_cmd.command("check")
@click.argument("project")
@click.argument("user")
@click.argument("role", type=click.Choice(acl_lib.ROLES))
@click.pass_context
def check_cmd(ctx: click.Context, project: str, user: str, role: str) -> None:
    """Check whether USER has at least ROLE on PROJECT."""
    storage_dir = _storage(ctx)
    try:
        allowed = acl_lib.check_permission(storage_dir, project, user, role)
    except acl_lib.ACLError as exc:
        raise click.ClickException(str(exc)) from exc
    if allowed:
        click.echo(f"'{user}' has '{role}' access on '{project}'.")
    else:
        click.echo(f"'{user}' does NOT have '{role}' access on '{project}'.")
        raise SystemExit(1)
