"""CLI commands for the labels feature."""
from __future__ import annotations

import os
import click

from envault.labels import (
    LabelError,
    add_label,
    remove_label,
    get_labels,
    find_by_label,
    clear_labels,
)

_DEFAULT_STORAGE = os.path.join(os.path.expanduser("~"), ".envault")


def _storage() -> str:
    return os.environ.get("ENVAULT_STORAGE", _DEFAULT_STORAGE)


@click.group("labels")
def labels_cmd():
    """Manage project labels."""


@labels_cmd.command("add")
@click.argument("project")
@click.argument("label")
def add_cmd(project: str, label: str):
    """Attach LABEL to PROJECT."""
    try:
        labels = add_label(_storage(), project, label)
        click.echo(f"Labels for '{project}': {', '.join(labels)}")
    except LabelError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@labels_cmd.command("remove")
@click.argument("project")
@click.argument("label")
def remove_cmd(project: str, label: str):
    """Detach LABEL from PROJECT."""
    try:
        labels = remove_label(_storage(), project, label)
        remaining = ", ".join(labels) if labels else "(none)"
        click.echo(f"Labels for '{project}': {remaining}")
    except LabelError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@labels_cmd.command("list")
@click.argument("project")
def list_cmd(project: str):
    """List labels attached to PROJECT."""
    labels = get_labels(_storage(), project)
    if not labels:
        click.echo(f"No labels for '{project}'.")
    else:
        for label in labels:
            click.echo(label)


@labels_cmd.command("find")
@click.argument("label")
def find_cmd(label: str):
    """Find all projects carrying LABEL."""
    projects = find_by_label(_storage(), label)
    if not projects:
        click.echo(f"No projects found with label '{label}'.")
    else:
        for proj in projects:
            click.echo(proj)


@labels_cmd.command("clear")
@click.argument("project")
def clear_cmd(project: str):
    """Remove all labels from PROJECT."""
    clear_labels(_storage(), project)
    click.echo(f"All labels cleared for '{project}'.")
