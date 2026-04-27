"""CLI entry point for envault using Click."""

import sys
import click
from envault.storage import save_env, load_env, list_projects, delete_env


@click.group()
def cli():
    """envault — securely manage and sync .env files."""
    pass


@cli.command("set")
@click.argument("project")
@click.option("--file", "-f", "env_file", default=".env", show_default=True,
              help="Path to the .env file to encrypt and store.")
@click.password_option("--passphrase", "-p", prompt="Passphrase",
                       help="Passphrase used to encrypt the data.")
def set_env(project, env_file, passphrase):
    """Encrypt and store a .env file for PROJECT."""
    try:
        with open(env_file, "rb") as fh:
            raw = fh.read()
    except FileNotFoundError:
        click.echo(f"Error: file '{env_file}' not found.", err=True)
        sys.exit(1)

    save_env(project, raw, passphrase)
    click.echo(f"Stored env for project '{project}'.")


@cli.command("get")
@click.argument("project")
@click.option("--output", "-o", default=".env", show_default=True,
              help="Destination file to write decrypted content.")
@click.option("--passphrase", "-p", prompt="Passphrase", hide_input=True,
              help="Passphrase used to decrypt the data.")
def get_env(project, output, passphrase):
    """Decrypt and restore the .env file for PROJECT."""
    try:
        data = load_env(project, passphrase)
    except KeyError:
        click.echo(f"Error: no stored env found for project '{project}'.", err=True)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    with open(output, "wb") as fh:
        fh.write(data)
    click.echo(f"Wrote decrypted env to '{output}'.")


@cli.command("list")
def list_envs():
    """List all projects with stored env files."""
    projects = list_projects()
    if not projects:
        click.echo("No projects stored yet.")
    else:
        click.echo("Stored projects:")
        for name in sorted(projects):
            click.echo(f"  - {name}")


@cli.command("delete")
@click.argument("project")
@click.confirmation_option(prompt="Are you sure you want to delete this env?")
def delete_env_cmd(project):
    """Delete the stored env for PROJECT."""
    try:
        delete_env(project)
        click.echo(f"Deleted env for project '{project}'.")
    except KeyError:
        click.echo(f"Error: no stored env found for project '{project}'.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
