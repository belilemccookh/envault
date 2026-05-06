"""Main CLI entry-point for envault."""
from __future__ import annotations

import click

from envault.storage import save_env, load_env, list_projects, delete_env
from envault.export import export_env, import_env
from envault.cli_export import export_cmd, import_cmd, dump_cmd
from envault.cli_share import share_export_cmd, share_import_cmd
from envault.cli_diff import diff_cmd
from envault.cli_history import history_cmd
from envault.cli_tags import tags_cmd
from envault.cli_templates import templates_cmd
from envault.cli_lock import lock_cmd
from envault.cli_notes import notes_cmd
from envault.cli_reminders import reminders_cmd


@click.group()
def cli():
    """envault — secure .env manager."""


@cli.command("set")
@click.argument("project")
@click.argument("file", type=click.Path(exists=True))
@click.password_option("--passphrase", "-p", help="Encryption passphrase.")
def set_env(project: str, file: str, passphrase: str) -> None:
    """Encrypt and store FILE as PROJECT."""
    import pathlib
    raw = pathlib.Path(file).read_text()
    save_env(project, raw, passphrase)
    click.echo(f"Stored '{project}'.")


@cli.command("get")
@click.argument("project")
@click.option("--passphrase", "-p", prompt=True, hide_input=True)
def get_env(project: str, passphrase: str) -> None:
    """Decrypt and print the env for PROJECT."""
    try:
        click.echo(load_env(project, passphrase))
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc


@cli.command("list")
def list_envs() -> None:
    """List stored projects."""
    projects = list_projects()
    if not projects:
        click.echo("No projects stored.")
    for p in projects:
        click.echo(p)


@cli.command("delete")
@click.argument("project")
@click.confirmation_option(prompt="Are you sure?")
def delete_env_cmd(project: str) -> None:
    """Delete PROJECT from storage."""
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
