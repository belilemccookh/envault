"""CLI commands for envault template management."""

from __future__ import annotations

import json
import sys

import click

from envault.templates import (
    TemplateError,
    apply_template,
    delete_template,
    list_templates,
    load_template,
    save_template,
)
from envault.storage import save_env, load_env


@click.group("template")
def templates_cmd():
    """Manage reusable env templates."""


@templates_cmd.command("save")
@click.argument("name")
@click.option("--from-project", "project", default=None, help="Seed template from a stored project.")
@click.option("--desc", default="", help="Short description of the template.")
@click.pass_context
def save_cmd(ctx, name, project, desc):
    """Save a new template, optionally seeded from an existing project."""
    passphrase = ctx.obj.get("passphrase", "") if ctx.obj else ""
    if project:
        try:
            keys = load_env(project, passphrase)
        except Exception as exc:
            click.echo(f"Error loading project: {exc}", err=True)
            sys.exit(1)
    else:
        keys = {}
    try:
        save_template(name, keys, description=desc)
        click.echo(f"Template '{name}' saved ({len(keys)} keys).")
    except TemplateError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@templates_cmd.command("list")
def list_cmd():
    """List all available templates."""
    templates = list_templates()
    if not templates:
        click.echo("No templates saved.")
        return
    for t in templates:
        desc = f"  — {t['description']}" if t["description"] else ""
        click.echo(f"{t['name']}{desc}")


@templates_cmd.command("show")
@click.argument("name")
def show_cmd(name):
    """Show keys defined in a template."""
    try:
        keys = load_template(name)
    except TemplateError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    for k, v in sorted(keys.items()):
        click.echo(f"{k}={v}")


@templates_cmd.command("apply")
@click.argument("name")
@click.argument("project")
@click.pass_context
def apply_cmd(ctx, name, project):
    """Apply a template to PROJECT (fills missing keys with template defaults)."""
    passphrase = ctx.obj.get("passphrase", "") if ctx.obj else ""
    try:
        existing = load_env(project, passphrase)
    except Exception:
        existing = {}
    try:
        merged = apply_template(name, overrides=existing)
        save_env(project, merged, passphrase)
        click.echo(f"Template '{name}' applied to '{project}' ({len(merged)} keys).")
    except TemplateError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@templates_cmd.command("delete")
@click.argument("name")
@click.confirmation_option(prompt="Delete this template?")
def delete_cmd(name):
    """Delete a saved template."""
    try:
        delete_template(name)
        click.echo(f"Template '{name}' deleted.")
    except TemplateError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
