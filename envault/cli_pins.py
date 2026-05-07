"""CLI commands for managing pinned (protected) env var keys."""

from __future__ import annotations

import click

from envault.pins import PinError, all_pins, get_pins, is_pinned, pin_key, unpin_key


@click.group("pins")
def pins_cmd() -> None:
    """Manage protected (pinned) keys for a project."""


@pins_cmd.command("add")
@click.argument("project")
@click.argument("key")
def add_cmd(project: str, key: str) -> None:
    """Pin KEY in PROJECT to mark it as protected."""
    try:
        pin_key(project, key)
        click.echo(f"Pinned '{key}' in project '{project}'.")
    except PinError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@pins_cmd.command("remove")
@click.argument("project")
@click.argument("key")
def remove_cmd(project: str, key: str) -> None:
    """Unpin KEY from PROJECT."""
    removed = unpin_key(project, key)
    if removed:
        click.echo(f"Unpinned '{key}' from project '{project}'.")
    else:
        click.echo(f"Key '{key}' was not pinned in project '{project}'.")


@pins_cmd.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List all pinned keys for PROJECT."""
    pins = get_pins(project)
    if not pins:
        click.echo(f"No pinned keys for project '{project}'.")
        return
    for key in pins:
        click.echo(key)


@pins_cmd.command("check")
@click.argument("project")
@click.argument("key")
def check_cmd(project: str, key: str) -> None:
    """Check whether KEY is pinned in PROJECT."""
    if is_pinned(project, key):
        click.echo(f"'{key}' is pinned in project '{project}'.")
    else:
        click.echo(f"'{key}' is NOT pinned in project '{project}'.")


@pins_cmd.command("all")
def all_cmd() -> None:
    """Show all pinned keys across every project."""
    data = all_pins()
    if not data:
        click.echo("No pins defined.")
        return
    for project, keys in sorted(data.items()):
        click.echo(f"{project}: {', '.join(keys)}")
