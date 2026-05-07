"""CLI commands for project groups."""

from __future__ import annotations

import click

from envault.groups import (
    GroupError,
    add_project,
    delete_group,
    get_group,
    list_groups,
    remove_project,
)


@click.group("groups")
def groups_cmd() -> None:
    """Organise projects into named groups."""


@groups_cmd.command("add")
@click.argument("group")
@click.argument("project")
def add_cmd(group: str, project: str) -> None:
    """Add PROJECT to GROUP."""
    try:
        members = add_project(group, project)
        click.echo(f"Added '{project}' to group '{group}'. Members: {', '.join(members)}")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@groups_cmd.command("remove")
@click.argument("group")
@click.argument("project")
def remove_cmd(group: str, project: str) -> None:
    """Remove PROJECT from GROUP."""
    try:
        members = remove_project(group, project)
        remaining = ", ".join(members) if members else "(empty)"
        click.echo(f"Removed '{project}' from group '{group}'. Remaining: {remaining}")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@groups_cmd.command("list")
def list_cmd() -> None:
    """List all groups and their projects."""
    data = list_groups()
    if not data:
        click.echo("No groups defined.")
        return
    for group, members in sorted(data.items()):
        click.echo(f"{group}: {', '.join(members)}")


@groups_cmd.command("show")
@click.argument("group")
def show_cmd(group: str) -> None:
    """Show members of GROUP."""
    try:
        members = get_group(group)
        click.echo(f"Group '{group}':")
        for m in members:
            click.echo(f"  - {m}")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@groups_cmd.command("delete")
@click.argument("group")
def delete_cmd(group: str) -> None:
    """Delete GROUP entirely."""
    try:
        delete_group(group)
        click.echo(f"Group '{group}' deleted.")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
