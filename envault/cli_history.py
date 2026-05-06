"""CLI commands for environment version history."""

from __future__ import annotations

import click

from envault.history import clear_history, get_snapshot, list_snapshots
from envault.storage import load_env, save_env


@click.group("history")
def history_cmd() -> None:
    """Manage environment version history."""


@history_cmd.command("list")
@click.argument("project")
def history_list_cmd(project: str) -> None:
    """List all snapshots for PROJECT."""
    snapshots = list_snapshots(project)
    if not snapshots:
        click.echo(f"No history found for '{project}'.")
        return
    for i, entry in enumerate(snapshots):
        note = f"  [{entry['note']}]" if entry.get("note") else ""
        key_count = len(entry["env"])
        click.echo(f"  {i:>3}  {entry['timestamp']}  {key_count} keys{note}")


@history_cmd.command("show")
@click.argument("project")
@click.argument("index", type=int, default=-1)
def history_show_cmd(project: str, index: int) -> None:
    """Show env keys for snapshot INDEX of PROJECT (default: latest)."""
    try:
        env = get_snapshot(project, index)
    except IndexError as exc:
        raise click.ClickException(str(exc)) from exc
    if not env:
        click.echo("(empty snapshot)")
        return
    for key, value in sorted(env.items()):
        click.echo(f"{key}={value}")


@history_cmd.command("restore")
@click.argument("project")
@click.argument("index", type=int)
@click.argument("passphrase")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def history_restore_cmd(project: str, index: int, passphrase: str, yes: bool) -> None:
    """Restore PROJECT to snapshot INDEX, re-encrypting with PASSPHRASE."""
    try:
        env = get_snapshot(project, index)
    except IndexError as exc:
        raise click.ClickException(str(exc)) from exc

    if not yes:
        click.confirm(
            f"Restore '{project}' to snapshot {index} ({len(env)} keys)?  This will overwrite the current data.",
            abort=True,
        )
    save_env(project, env, passphrase)
    click.echo(f"Restored '{project}' to snapshot {index}.")


@history_cmd.command("clear")
@click.argument("project")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def history_clear_cmd(project: str, yes: bool) -> None:
    """Delete all history for PROJECT."""
    if not yes:
        click.confirm(f"Delete all history for '{project}'?", abort=True)
    removed = clear_history(project)
    click.echo(f"Cleared {removed} snapshot(s) for '{project}'.")
