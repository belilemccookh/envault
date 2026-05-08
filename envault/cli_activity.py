"""CLI commands for viewing project activity statistics."""
from __future__ import annotations

import click

from envault.activity import ActivityError, all_activity, get_activity, reset_activity


@click.group("activity")
def activity_cmd() -> None:
    """View and manage project activity statistics."""


@activity_cmd.command("show")
@click.argument("project")
def show_cmd(project: str) -> None:
    """Show activity counters for PROJECT."""
    try:
        entry = get_activity(project)
    except ActivityError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Project : {project}")
    click.echo(f"  reads  : {entry['read']}")
    click.echo(f"  writes : {entry['write']}")
    click.echo(f"  deletes: {entry['delete']}")
    click.echo(f"  last   : {entry['last_seen'] or 'never'}")


@activity_cmd.command("list")
def list_cmd() -> None:
    """List activity for all projects."""
    data = all_activity()
    if not data:
        click.echo("No activity recorded yet.")
        return
    for project, entry in sorted(data.items()):
        click.echo(
            f"{project}: r={entry['read']} w={entry['write']} d={entry['delete']}"
            f"  last={entry['last_seen'] or 'never'}"
        )


@activity_cmd.command("reset")
@click.argument("project")
@click.confirmation_option(prompt="Reset activity for this project?")
def reset_cmd(project: str) -> None:
    """Reset activity counters for PROJECT."""
    try:
        reset_activity(project)
    except ActivityError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Activity reset for '{project}'.")
