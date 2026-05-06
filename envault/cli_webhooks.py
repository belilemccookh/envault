"""CLI commands for webhook management."""
from __future__ import annotations

import click

from envault.webhooks import WebhookError, list_hooks, notify, register, unregister


@click.group("webhooks")
def webhooks_cmd() -> None:
    """Manage webhook notifications for project events."""


@webhooks_cmd.command("add")
@click.argument("project")
@click.argument("url")
def add_cmd(project: str, url: str) -> None:
    """Register a webhook URL for PROJECT."""
    try:
        register(project, url)
        click.echo(f"Webhook registered for '{project}': {url}")
    except WebhookError as exc:
        raise click.ClickException(str(exc)) from exc


@webhooks_cmd.command("remove")
@click.argument("project")
@click.argument("url")
def remove_cmd(project: str, url: str) -> None:
    """Unregister a webhook URL from PROJECT."""
    removed = unregister(project, url)
    if removed:
        click.echo(f"Removed webhook from '{project}': {url}")
    else:
        click.echo(f"URL not found for '{project}': {url}")


@webhooks_cmd.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List all webhook URLs registered for PROJECT."""
    hooks = list_hooks(project)
    if not hooks:
        click.echo(f"No webhooks registered for '{project}'.")
        return
    for url in hooks:
        click.echo(url)


@webhooks_cmd.command("fire")
@click.argument("project")
@click.argument("event")
def fire_cmd(project: str, event: str) -> None:
    """Manually fire EVENT to all webhooks registered for PROJECT."""
    results = notify(project, event)
    if not results:
        click.echo(f"No webhooks registered for '{project}'.")
        return
    for url, ok, msg in results:
        status = click.style("OK", fg="green") if ok else click.style("FAIL", fg="red")
        click.echo(f"[{status}] {url} — {msg}")
