"""CLI commands for diffing stored env snapshots against files or other projects."""
from __future__ import annotations

import click

from .audit import record
from .diff import diff_envs, format_diff
from .export import dotenv_to_dict
from .storage import load_env


@click.command("diff")
@click.argument("project")
@click.option(
    "--file",
    "env_file",
    type=click.Path(exists=True),
    default=None,
    help="Compare stored env against a .env file.",
)
@click.option(
    "--against",
    "other_project",
    default=None,
    help="Compare stored env against another stored project.",
)
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--show-values", is_flag=True, default=False, help="Reveal actual values.")
def diff_cmd(
    project: str,
    env_file: str | None,
    other_project: str | None,
    passphrase: str,
    show_values: bool,
) -> None:
    """Show differences between a stored project env and a file or another project."""
    if env_file is None and other_project is None:
        raise click.UsageError("Provide --file or --against.")
    if env_file and other_project:
        raise click.UsageError("Use only one of --file or --against.")

    try:
        old = load_env(project, passphrase)
    except Exception as exc:  # noqa: BLE001
        record(project, "diff", success=False, detail=str(exc))
        raise click.ClickException(str(exc)) from exc

    try:
        if env_file:
            with open(env_file) as fh:
                new = dotenv_to_dict(fh.read())
            label = env_file
        else:
            new = load_env(other_project, passphrase)  # type: ignore[arg-type]
            label = other_project
    except Exception as exc:  # noqa: BLE001
        record(project, "diff", success=False, detail=str(exc))
        raise click.ClickException(str(exc)) from exc

    result = diff_envs(old, new)
    record(project, "diff", success=True, detail=f"compared against {label}")

    if not result.has_changes:
        click.echo("No differences found.")
        return

    click.echo(f"Diff: {project}  vs  {label}")
    click.echo(f"Summary: {result.summary}")
    click.echo("")
    for line in format_diff(result, mask_values=not show_values):
        click.echo(line)
