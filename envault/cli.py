"""Main CLI entry-point for envault."""
import click

from .audit import record
from .cli_diff import diff_cmd
from .cli_export import dump_cmd, export_cmd, import_cmd
from .cli_share import share_export_cmd, share_import_cmd
from .storage import delete_env, list_projects, load_env, save_env


@click.group()
def cli() -> None:
    """envault – secure .env manager."""


@cli.command("set")
@click.argument("project")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True, confirmation_prompt=True)
def set_env(project: str, env_file: str, passphrase: str) -> None:
    """Store an env file for PROJECT."""
    try:
        with open(env_file) as fh:
            raw = fh.read()
        save_env(project, raw, passphrase)
        record(project, "set", success=True)
        click.echo(f"Stored env for '{project}'.")
    except Exception as exc:  # noqa: BLE001
        record(project, "set", success=False, detail=str(exc))
        raise click.ClickException(str(exc)) from exc


@cli.command("get")
@click.argument("project")
@click.option("--passphrase", prompt=True, hide_input=True)
def get_env(project: str, passphrase: str) -> None:
    """Print the stored env for PROJECT."""
    try:
        data = load_env(project, passphrase)
        record(project, "get", success=True)
        for k, v in data.items():
            click.echo(f"{k}={v}")
    except Exception as exc:  # noqa: BLE001
        record(project, "get", success=False, detail=str(exc))
        raise click.ClickException(str(exc)) from exc


@cli.command("list")
def list_envs() -> None:
    """List all stored projects."""
    projects = list_projects()
    if not projects:
        click.echo("No projects stored.")
    for p in projects:
        click.echo(p)


@cli.command("delete")
@click.argument("project")
@click.confirmation_option(prompt="Are you sure?")
def delete_env_cmd(project: str) -> None:
    """Delete the stored env for PROJECT."""
    try:
        delete_env(project)
        record(project, "delete", success=True)
        click.echo(f"Deleted env for '{project}'.")
    except Exception as exc:  # noqa: BLE001
        record(project, "delete", success=False, detail=str(exc))
        raise click.ClickException(str(exc)) from exc


cli.add_command(export_cmd, "export")
cli.add_command(import_cmd, "import")
cli.add_command(dump_cmd, "dump")
cli.add_command(share_export_cmd, "share-export")
cli.add_command(share_import_cmd, "share-import")
cli.add_command(diff_cmd, "diff")
