"""Main CLI entry-point for envault."""

from __future__ import annotations

import click

from envault.storage import save_env, load_env, list_projects, delete_env
from envault.cli_export import export_cmd, import_cmd, dump_cmd
from envault.cli_share import share_export_cmd, share_import_cmd
from envault.cli_diff import diff_cmd
from envault.cli_history import history_cmd
from envault.cli_tags import tags_cmd
from envault.cli_templates import templates_cmd
from envault.cli_lock import lock_cmd


@click.group()
def cli() -> None:
    """envault — secure .env management."""


# ---------------------------------------------------------------------------
# Core commands
# ---------------------------------------------------------------------------

@cli.command("set")
@click.argument("project")
@click.argument("file", type=click.Path(exists=True))
@click.password_option("--passphrase", prompt="Passphrase")
def set_env(project: str, file: str, passphrase: str) -> None:
    """Encrypt and store FILE under PROJECT."""
    from envault.export import dotenv_to_dict
    with open(file) as fh:
        data = dotenv_to_dict(fh.read())
    save_env(project, data, passphrase)
    click.echo(f"✅  Stored {len(data)} key(s) for '{project}'.")


@cli.command("get")
@click.argument("project")
@click.argument("key")
@click.password_option("--passphrase", prompt="Passphrase", confirmation_prompt=False)
def get_env(project: str, key: str, passphrase: str) -> None:
    """Retrieve a single KEY from PROJECT."""
    data = load_env(project, passphrase)
    if key not in data:
        raise click.ClickException(f"Key '{key}' not found in '{project}'.")
    click.echo(data[key])


@cli.command("list")
def list_envs() -> None:
    """List all stored projects."""
    projects = list_projects()
    if not projects:
        click.echo("No projects stored.")
        return
    for p in sorted(projects):
        click.echo(p)


@cli.command("delete")
@click.argument("project")
@click.confirmation_option(prompt="Are you sure?")
def delete_env_cmd(project: str) -> None:
    """Delete a stored project."""
    delete_env(project)
    click.echo(f"🗑️  Deleted '{project}'.")


# ---------------------------------------------------------------------------
# Sub-command groups
# ---------------------------------------------------------------------------

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
