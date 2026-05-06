"""Main CLI entry-point for envault."""
from __future__ import annotations

import click

from envault.storage import delete_env, list_projects, load_env, save_env
from envault.cli_export import export_cmd, import_cmd, dump_cmd
from envault.cli_share import share_export_cmd, share_import_cmd
from envault.cli_diff import diff_cmd
from envault.cli_history import history_cmd
from envault.cli_tags import tags_cmd
from envault.cli_templates import templates_cmd
from envault.cli_lock import lock_cmd
from envault.cli_notes import notes_cmd
from envault.cli_reminders import reminders_cmd
from envault.cli_webhooks import webhooks_cmd
from envault.cli_aliases import aliases_cmd
from envault.cli_snapshots import snapshots_cmd


@click.group()
def cli() -> None:
    """envault — secure .env manager."""


@cli.command()
@click.argument("project")
@click.argument("file", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True)
def set_env(project: str, file: str, passphrase: str) -> None:
    """Store a .env FILE under PROJECT."""
    import dotenv
    env = dict(dotenv.dotenv_values(file))
    save_env(project, env, passphrase)
    click.echo(f"Stored {len(env)} variable(s) for '{project}'.")


@cli.command()
@click.argument("project")
@click.option("--passphrase", prompt=True, hide_input=True)
def get_env(project: str, passphrase: str) -> None:
    """Print env variables for PROJECT."""
    env = load_env(project, passphrase)
    for k, v in sorted(env.items()):
        click.echo(f"{k}={v}")


@cli.command(name="list")
def list_envs() -> None:
    """List all stored projects."""
    projects = list_projects()
    if not projects:
        click.echo("No projects stored.")
        return
    for p in projects:
        click.echo(f"  {p}")


@cli.command(name="delete")
@click.argument("project")
@click.confirmation_option(prompt="Delete this project?")
def delete_env_cmd(project: str) -> None:
    """Delete a stored project."""
    delete_env(project)
    click.echo(f"Deleted '{project}'.")


cli.add_command(export_cmd, "export")
cli.add_command(import_cmd, "import")
cli.add_command(dump_cmd, "dump")
cli.add_command(share_export_cmd, "share-export")
cli.add_command(share_import_cmd, "share-import")
cli.add_command(diff_cmd, "diff")
cli.add_command(history_cmd, "history")
cli.add_command(tags_cmd, "tags")
cli.add_command(templates_cmd, "templates")
cli.add_command(lock_cmd, "lock")
cli.add_command(notes_cmd, "notes")
cli.add_command(reminders_cmd, "reminders")
cli.add_command(webhooks_cmd, "webhooks")
cli.add_command(aliases_cmd, "aliases")
cli.add_command(snapshots_cmd, "snapshots")
