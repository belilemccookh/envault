"""CLI commands for project tag management."""
from __future__ import annotations

import click

from envault import tags as tag_lib


@click.group("tags")
def tags_cmd() -> None:
    """Manage tags on projects."""


@tags_cmd.command("add")
@click.argument("project")
@click.argument("tag")
def add_cmd(project: str, tag: str) -> None:
    """Add TAG to PROJECT."""
    tag_lib.add_tag(project, tag)
    click.echo(f"Tagged '{project}' with '{tag.strip().lower()}'.")


@tags_cmd.command("remove")
@click.argument("project")
@click.argument("tag")
def remove_cmd(project: str, tag: str) -> None:
    """Remove TAG from PROJECT."""
    removed = tag_lib.remove_tag(project, tag)
    if removed:
        click.echo(f"Removed tag '{tag.strip().lower()}' from '{project}'.")
    else:
        click.echo(
            f"Tag '{tag.strip().lower()}' not found on '{project}'.", err=True
        )
        raise SystemExit(1)


@tags_cmd.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List tags for PROJECT."""
    project_tags = tag_lib.get_tags(project)
    if project_tags:
        for t in project_tags:
            click.echo(t)
    else:
        click.echo(f"No tags for '{project}'.")


@tags_cmd.command("find")
@click.argument("tag")
def find_cmd(tag: str) -> None:
    """Find all projects carrying TAG."""
    projects = tag_lib.projects_with_tag(tag)
    if projects:
        for p in projects:
            click.echo(p)
    else:
        click.echo(f"No projects tagged '{tag.strip().lower()}'.")


@tags_cmd.command("clear")
@click.argument("project")
@click.confirmation_option(prompt="Remove all tags for this project?")
def clear_cmd(project: str) -> None:
    """Remove all tags from PROJECT."""
    tag_lib.clear_tags(project)
    click.echo(f"All tags cleared for '{project}'.")


@tags_cmd.command("rename")
@click.argument("old_tag")
@click.argument("new_tag")
def rename_cmd(old_tag: str, new_tag: str) -> None:
    """Rename OLD_TAG to NEW_TAG across all projects."""
    projects = tag_lib.projects_with_tag(old_tag)
    if not projects:
        click.echo(f"Tag '{old_tag.strip().lower()}' not found on any project.", err=True)
        raise SystemExit(1)
    for project in projects:
        tag_lib.remove_tag(project, old_tag)
        tag_lib.add_tag(project, new_tag)
    click.echo(
        f"Renamed tag '{old_tag.strip().lower()}' to '{new_tag.strip().lower()}' "
        f"across {len(projects)} project(s)."
    )
