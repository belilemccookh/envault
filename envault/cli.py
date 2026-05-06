"""Main CLI entry-point for envault."""

from __future__ import annotations

import sys

import click

from envault.storage import save_env, load_env, list_projects, delete_env
from envault.cli_export import export_cmd, import_cmd, dump_cmd
from envault.cli_share import share_export_cmd, share_import_cmd
from envault.cli_diff import diff_cmd
from envault.cli_history import history_cmd
from envault.cli_tags import tags_cmd
from envault.cli_templates import templates_cmd


@click.group()
@click.option("--passphrase", envvar="ENVAULT_PASSPHRASE", default="", show_default=False,
              help="Master passphrase (or set ENVAULT_PASSPHRASE).")
@click.pass_context
def cli(ctx, passphrase):
    """envault — secure .env manager."""
    ctx.ensure_object(dict)
    ctx.obj["passphrase"] = passphrase


@cli.command("set")
@click.argument("project")
@click.argument("env_file", type=click.Path(exists=True))
@click.pass_context
def set_env(ctx, project, env_file):
    """Store an .env file under PROJECT."""
    from envault.export import dotenv_to_dict
    passphrase = ctx.obj["passphrase"]
    with open(env_file) as fh:
        env = dotenv_to_dict(fh.read())
    save_env(project, env, passphrase)
    click.echo(f"Stored {len(env)} keys for '{project}'.")


@cli.command("get")
@click.argument("project")
@click.argument("key")
@click.pass_context
def get_env(ctx, project, key):
    """Retrieve a single KEY from PROJECT."""
    passphrase = ctx.obj["passphrase"]
    try:
        env = load_env(project, passphrase)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    if key not in env:
        click.echo(f"Key '{key}' not found.", err=True)
        sys.exit(1)
    click.echo(env[key])


@cli.command("list")
def list_envs():
    """List all stored projects."""
    projects = list_projects()
    if not projects:
        click.echo("No projects stored.")
    for p in projects:
        click.echo(p)


@cli.command("delete")
@click.argument("project")
@click.confirmation_option(prompt="Delete this project?")
def delete_env_cmd(project):
    """Delete a stored project."""
    try:
        delete_env(project)
        click.echo(f"Deleted '{project}'.")
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


cli.add_command(export_cmd, "export")
cli.add_command(import_cmd, "import")
cli.add_command(dump_cmd, "dump")
cli.add_command(share_export_cmd, "share-export")
cli.add_command(share_import_cmd, "share-import")
cli.add_command(diff_cmd, "diff")
cli.add_command(history_cmd, "history")
cli.add_command(tags_cmd, "tags")
cli.add_command(templates_cmd, "template")
