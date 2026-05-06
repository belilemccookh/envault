"""CLI commands for project notes."""

from __future__ import annotations

import click

from envault import notes as notes_lib


@click.group("notes")
def notes_cmd() -> None:
    """Manage plain-text notes attached to a project."""


@notes_cmd.command("add")
@click.argument("project")
@click.argument("text")
def add_cmd(project: str, text: str) -> None:
    """Add a note to PROJECT."""
    try:
        entry = notes_lib.add_note(project, text)
        click.echo(f"Note #{entry['id']} added to '{project}' at {entry['ts']}.")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@notes_cmd.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List all notes for PROJECT."""
    entries = notes_lib.list_notes(project)
    if not entries:
        click.echo(f"No notes for '{project}'.")
        return
    for entry in entries:
        click.echo(f"[{entry['id']}] {entry['ts']}  {entry['text']}")


@notes_cmd.command("show")
@click.argument("project")
@click.argument("note_id", type=int)
def show_cmd(project: str, note_id: int) -> None:
    """Show a single note by NOTE_ID."""
    entry = notes_lib.get_note(project, note_id)
    if entry is None:
        raise click.ClickException(f"Note #{note_id} not found in '{project}'.")
    click.echo(f"[{entry['id']}] {entry['ts']}\n{entry['text']}")


@notes_cmd.command("delete")
@click.argument("project")
@click.argument("note_id", type=int)
def delete_cmd(project: str, note_id: int) -> None:
    """Delete note NOTE_ID from PROJECT."""
    removed = notes_lib.delete_note(project, note_id)
    if removed:
        click.echo(f"Note #{note_id} deleted from '{project}'.")
    else:
        raise click.ClickException(f"Note #{note_id} not found in '{project}'.")


@notes_cmd.command("clear")
@click.argument("project")
@click.confirmation_option(prompt="Delete ALL notes for this project?")
def clear_cmd(project: str) -> None:
    """Remove all notes for PROJECT."""
    count = notes_lib.clear_notes(project)
    click.echo(f"Cleared {count} note(s) from '{project}'.")
