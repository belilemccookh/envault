"""CLI commands for exporting and importing envault project bundles."""

from __future__ import annotations

import click

from envault.export import env_to_dotenv, export_env, import_env, load_env


@click.command("export")
@click.argument("project")
@click.argument("output", type=click.Path(dir_okay=False, writable=True))
@click.password_option("--passphrase", prompt="Passphrase", help="Encryption passphrase")
def export_cmd(project: str, output: str, passphrase: str) -> None:
    """Export PROJECT's encrypted env bundle to OUTPUT file."""
    try:
        export_env(project, passphrase, output)
        click.echo(f"Exported '{project}' to {output}")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@click.command("import")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--project", default=None, help="Override project name from bundle")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing project")
@click.password_option("--passphrase", prompt="Passphrase", help="Encryption passphrase")
def import_cmd(
    input_file: str, project: str | None, overwrite: bool, passphrase: str
) -> None:
    """Import an encrypted env bundle from INPUT_FILE."""
    try:
        imported = import_env(input_file, passphrase, project_override=project, overwrite=overwrite)
        click.echo(f"Imported project '{imported}' successfully.")
    except FileExistsError as exc:
        raise click.ClickException(
            str(exc) + " Pass --overwrite to replace."
        ) from exc
    except (ValueError, FileNotFoundError) as exc:
        raise click.ClickException(str(exc)) from exc


@click.command("dump")
@click.argument("project")
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Write to file instead of stdout",
)
@click.password_option("--passphrase", prompt="Passphrase", help="Encryption passphrase")
def dump_cmd(project: str, output: str | None, passphrase: str) -> None:
    """Dump PROJECT env vars as a plain .env file to stdout or OUTPUT."""
    env_vars = load_env(project, passphrase)
    if env_vars is None:
        raise click.ClickException(f"Project '{project}' not found.")

    dotenv_content = env_to_dotenv(env_vars)

    if output:
        with open(output, "w") as fh:
            fh.write(dotenv_content)
        click.echo(f"Written {len(env_vars)} variable(s) to {output}")
    else:
        click.echo(dotenv_content, nl=False)
