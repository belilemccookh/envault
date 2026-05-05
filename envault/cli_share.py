"""CLI commands for sharing encrypted env bundles."""

from __future__ import annotations

from pathlib import Path

import click

from envault.share import ShareError, export_bundle, import_bundle


@click.command("share-export")
@click.argument("project")
@click.option("--passphrase", prompt=True, hide_input=True, help="Master vault passphrase.")
@click.option(
    "--share-passphrase",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Passphrase to protect the bundle.",
)
@click.option(
    "--output", "-o", default=None, help="Output file path (default: <project>.envbundle)."
)
def share_export_cmd(project: str, passphrase: str, share_passphrase: str, output: str) -> None:
    """Export PROJECT as an encrypted shareable bundle."""
    out_path = Path(output) if output else None
    try:
        saved = export_bundle(project, passphrase, share_passphrase, out_path)
        click.echo(f"Bundle written to: {saved}")
    except ShareError as exc:
        raise click.ClickException(str(exc)) from exc


@click.command("share-import")
@click.argument("bundle_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--share-passphrase", prompt=True, hide_input=True, help="Bundle passphrase.")
@click.option(
    "--passphrase", prompt=True, hide_input=True, help="Master vault passphrase for storage."
)
@click.option("--project", default=None, help="Override project name from bundle.")
def share_import_cmd(
    bundle_file: str, share_passphrase: str, passphrase: str, project: str
) -> None:
    """Import an encrypted bundle into the local vault."""
    try:
        name = import_bundle(Path(bundle_file), share_passphrase, passphrase, project)
        click.echo(f"Imported project '{name}' successfully.")
    except ShareError as exc:
        raise click.ClickException(str(exc)) from exc
