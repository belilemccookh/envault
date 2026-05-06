"""CLI commands for managing rotation reminders."""
from __future__ import annotations

import click

from envault.reminders import (
    ReminderError,
    delete_reminder,
    due_reminders,
    get_reminder,
    list_reminders,
    set_reminder,
)


@click.group("reminders")
def reminders_cmd():
    """Manage rotation reminders for projects."""


@reminders_cmd.command("set")
@click.argument("project")
@click.option("--days", "-d", default=30, show_default=True, help="Days until reminder.")
@click.option("--note", "-n", default="", help="Optional reminder note.")
def set_cmd(project: str, days: int, note: str) -> None:
    """Set a rotation reminder for PROJECT."""
    try:
        entry = set_reminder(project, days, note)
        click.echo(f"Reminder set for '{project}' — due {entry['due']} UTC")
    except ReminderError as exc:
        raise click.ClickException(str(exc)) from exc


@reminders_cmd.command("show")
@click.argument("project")
def show_cmd(project: str) -> None:
    """Show the reminder for PROJECT."""
    entry = get_reminder(project)
    if entry is None:
        click.echo(f"No reminder set for '{project}'.")
        return
    click.echo(f"Project : {entry['project']}")
    click.echo(f"Due     : {entry['due']} UTC")
    click.echo(f"Created : {entry['created']} UTC")
    if entry.get("note"):
        click.echo(f"Note    : {entry['note']}")


@reminders_cmd.command("list")
@click.option("--due-only", is_flag=True, help="Only show overdue reminders.")
def list_cmd(due_only: bool) -> None:
    """List all reminders."""
    items = due_reminders() if due_only else list_reminders()
    if not items:
        click.echo("No reminders found.")
        return
    for r in items:
        tag = " [DUE]" if r["due"] <= __import__("envault.reminders", fromlist=["_now_iso"]).reminders._now_iso() else ""
        click.echo(f"{r['project']:30s}  {r['due']} UTC{tag}")


@reminders_cmd.command("delete")
@click.argument("project")
def delete_cmd(project: str) -> None:
    """Delete the reminder for PROJECT."""
    removed = delete_reminder(project)
    if removed:
        click.echo(f"Reminder for '{project}' deleted.")
    else:
        click.echo(f"No reminder found for '{project}'.")
