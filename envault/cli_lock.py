"""CLI commands for inspecting and managing project locks."""

import click

from envault import lock as locklib
from envault.storage import list_projects


@click.group("lock")
def lock_cmd() -> None:
    """Manage project locks."""


@lock_cmd.command("status")
@click.argument("project")
def status_cmd(project: str) -> None:
    """Show lock status for PROJECT."""
    if locklib.is_locked(project):
        owner = locklib._lock_owner(locklib._lock_path(project))
        click.echo(f"🔒  '{project}' is locked (PID {owner}).")
    else:
        click.echo(f"✅  '{project}' is not locked.")


@lock_cmd.command("release")
@click.argument("project")
def release_cmd(project: str) -> None:
    """Forcefully release the lock on PROJECT."""
    if not locklib.is_locked(project):
        click.echo(f"'{project}' is not locked — nothing to do.")
        return
    locklib.release(project)
    click.echo(f"🔓  Lock on '{project}' released.")


@lock_cmd.command("list")
def list_cmd() -> None:
    """List all projects that currently hold a lock."""
    projects = list_projects()
    locked = [p for p in projects if locklib.is_locked(p)]
    if not locked:
        click.echo("No projects are currently locked.")
        return
    click.echo(f"{'Project':<30}  Lock owner (PID)")
    click.echo("-" * 48)
    for p in locked:
        owner = locklib._lock_owner(locklib._lock_path(p))
        click.echo(f"{p:<30}  {owner}")
