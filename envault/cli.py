"""Main CLI entry-point for envault."""

from __future__ import annotations

import click

from envault.storage import load_env, save_env, list_projects, delete_env
from envault.audit import record
from envault.cli_export import export_cmd, import_cmd, dump_cmd
from envault.cli_share import share_export_cmd, share_import_cmd


@click.group()
def cli() -> None:
    """envault — secure .env manager."""


@cli.command("set")
@click.argument("project")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True)
def set_env(project: str, env_file: str, passphrase: str) -> None:
    """Store env vars from ENV_FILE under PROJECT."""
    from envault.export import dotenv_to_dict
    from pathlib import Path

    env = dotenv_to_dict(Path(env_file).read_text())
    save_env(project, env, passphrase)
    record(project, "set", success=True)
    click.echo(f"Stored {len(env)} variable(s) for project '{project}'.")


@cli.command("get")
@click.argument("project")
@click.argument("key")
@click.option("--passphrase", prompt=True, hide_input=True)
def get_env(project: str, key: str, passphrase: str) -> None:
    """Print the value of KEY in PROJECT."""
    env = load_env(project, passphrase)
    if env is None:
        record(project, "get", success=False)
        raise click.ClickException(f"Project '{project}' not found or wrong passphrase.")
    if key not in env:
        raise click.ClickException(f"Key '{key}' not found in project '{project}'.")
    record(project, "get", success=True)
    click.echo(env[key])


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
@click.option("--passphrase", prompt=True, hide_input=True)
@click.confirmation_option(prompt="Are you sure you want to delete this project?")
def delete_env_cmd(project: str, passphrase: str) -> None:
    """Delete a stored project."""
    env = load_env(project, passphrase)
    if env is None:
        raise click.ClickException(f"Project '{project}' not found or wrong passphrase.")
    delete_env(project)
    record(project, "delete", success=True)
    click.echo(f"Deleted project '{project}'.")


cli.add_command(export_cmd)
cli.add_command(import_cmd)
cli.add_command(dump_cmd)
cli.add_command(share_export_cmd)
cli.add_command(share_import_cmd)
