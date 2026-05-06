"""CLI commands for named project snapshots."""
from __future__ import annotations

import click

from envault.snapshots import (
    SnapshotError,
    create_snapshot,
    delete_snapshot,
    get_snapshot,
    list_snapshots,
)
from envault.storage import load_env


@click.group("snapshots")
def snapshots_cmd() -> None:
    """Manage named snapshots of a project's environment."""


@snapshots_cmd.command("create")
@click.argument("project")
@click.argument("label")
@click.option("--passphrase", prompt=True, hide_input=True, help="Vault passphrase.")
def create_cmd(project: str, label: str, passphrase: str) -> None:
    """Create a named snapshot of PROJECT's current env."""
    try:
        env = load_env(project, passphrase)
        entry = create_snapshot(project, label, env)
        click.echo(f"Snapshot #{entry['id']} '{label}' created for '{project}'.")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@snapshots_cmd.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List all snapshots for PROJECT."""
    entries = list_snapshots(project)
    if not entries:
        click.echo(f"No snapshots found for '{project}'.")
        return
    for e in entries:
        click.echo(f"  #{e['id']:>3}  {e['label']:<30}  {e['created_at']}")


@snapshots_cmd.command("show")
@click.argument("project")
@click.argument("snapshot_id", type=int)
def show_cmd(project: str, snapshot_id: int) -> None:
    """Show the env stored in a snapshot."""
    try:
        entry = get_snapshot(project, snapshot_id)
        click.echo(f"Snapshot #{entry['id']} — {entry['label']} ({entry['created_at']})")
        for k, v in sorted(entry["env"].items()):
            click.echo(f"  {k}={v}")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@snapshots_cmd.command("delete")
@click.argument("project")
@click.argument("snapshot_id", type=int)
@click.confirmation_option(prompt="Delete this snapshot?")
def delete_cmd(project: str, snapshot_id: int) -> None:
    """Delete a snapshot by ID."""
    try:
        delete_snapshot(project, snapshot_id)
        click.echo(f"Snapshot #{snapshot_id} deleted.")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
