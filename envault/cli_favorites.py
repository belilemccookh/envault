"""CLI commands for the favorites feature."""
from __future__ import annotations

import click

from envault import favorites as fav_lib
from envault.favorites import FavoriteError


@click.group("favorites")
def favorites_cmd() -> None:
    """Manage favourite projects for quick access."""


@favorites_cmd.command("add")
@click.argument("project")
def add_cmd(project: str) -> None:
    """Add PROJECT to favorites."""
    try:
        fav_lib.add_favorite(project)
        click.echo(f"Added '{project}' to favorites.")
    except FavoriteError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@favorites_cmd.command("remove")
@click.argument("project")
def remove_cmd(project: str) -> None:
    """Remove PROJECT from favorites."""
    try:
        fav_lib.remove_favorite(project)
        click.echo(f"Removed '{project}' from favorites.")
    except FavoriteError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@favorites_cmd.command("list")
def list_cmd() -> None:
    """List all favorited projects."""
    favs = fav_lib.list_favorites()
    if not favs:
        click.echo("No favorites saved.")
        return
    for name in favs:
        click.echo(f"  ★  {name}")


@favorites_cmd.command("check")
@click.argument("project")
def check_cmd(project: str) -> None:
    """Check whether PROJECT is a favorite."""
    if fav_lib.is_favorite(project):
        click.echo(f"'{project}' is a favorite.")
    else:
        click.echo(f"'{project}' is NOT a favorite.")


@favorites_cmd.command("clear")
def clear_cmd() -> None:
    """Remove all favorites."""
    count = fav_lib.clear_favorites()
    click.echo(f"Cleared {count} favorite(s).")
