"""CLI commands for project alias management."""

from __future__ import annotations

import click

from envault.aliases import (
    AliasError,
    set_alias,
    remove_alias,
    resolve,
    list_aliases,
)


@click.group("alias")
def aliases_cmd() -> None:
    """Manage short aliases for project names."""


@aliases_cmd.command("set")
@click.argument("alias")
@click.argument("project")
def set_cmd(alias: str, project: str) -> None:
    """Create or update ALIAS pointing to PROJECT."""
    try:
        set_alias(alias, project)
        click.echo(f"Alias '{alias}' → '{project}' saved.")
    except AliasError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@aliases_cmd.command("remove")
@click.argument("alias")
def remove_cmd(alias: str) -> None:
    """Delete ALIAS."""
    try:
        remove_alias(alias)
        click.echo(f"Alias '{alias}' removed.")
    except AliasError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@aliases_cmd.command("show")
@click.argument("alias")
def show_cmd(alias: str) -> None:
    """Show the project that ALIAS resolves to."""
    project = resolve(alias)
    if project is None:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    click.echo(project)


@aliases_cmd.command("list")
def list_cmd() -> None:
    """List all defined aliases."""
    mapping = list_aliases()
    if not mapping:
        click.echo("No aliases defined.")
        return
    width = max(len(k) for k in mapping)
    for alias, project in sorted(mapping.items()):
        click.echo(f"  {alias:<{width}}  →  {project}")
