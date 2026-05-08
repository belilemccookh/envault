"""CLI commands for displaying project metrics."""

from __future__ import annotations

import click

from envault.metrics import MetricsError, all_metrics, project_metrics, summary


@click.group("metrics")
def metrics_cmd() -> None:
    """Inspect key counts and storage stats."""


@metrics_cmd.command("show")
@click.argument("project")
@click.option("--passphrase", envvar="ENVAULT_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--keys", is_flag=True, default=False, help="List individual key names.")
def show_cmd(project: str, passphrase: str, keys: bool) -> None:
    """Show metrics for PROJECT."""
    try:
        m = project_metrics(project, passphrase)
    except MetricsError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Project      : {m.project}")
    click.echo(f"Keys         : {m.key_count}")
    click.echo(f"Size (bytes) : {m.size_bytes}")
    click.echo(f"Last modified: {m.last_modified}")
    if keys and m.keys:
        click.echo("Key names    :")
        for k in m.keys:
            click.echo(f"  {k}")


@metrics_cmd.command("summary")
@click.option("--passphrase", envvar="ENVAULT_PASSPHRASE", prompt=True, hide_input=True)
def summary_cmd(passphrase: str) -> None:
    """Show aggregate metrics across all projects."""
    metrics = all_metrics(passphrase)
    if not metrics:
        click.echo("No projects found.")
        return

    totals = summary(metrics)
    click.echo(f"Projects : {totals['total_projects']}")
    click.echo(f"Keys     : {totals['total_keys']}")
    click.echo(f"Storage  : {totals['total_bytes']} bytes")
    click.echo()
    click.echo(f"{'Project':<30} {'Keys':>6} {'Bytes':>8}  Last Modified")
    click.echo("-" * 70)
    for m in metrics:
        click.echo(f"{m.project:<30} {m.key_count:>6} {m.size_bytes:>8}  {m.last_modified}")
