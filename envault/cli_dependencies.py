"""CLI commands for managing inter-project dependencies."""

from __future__ import annotations

import click

from envault.dependencies import (
    DependencyError,
    add_dependency,
    all_dependencies,
    list_dependencies,
    list_dependents,
    remove_dependency,
)


@click.group("deps")
def deps_cmd() -> None:
    """Manage inter-project dependencies."""


@deps_cmd.command("add")
@click.argument("project")
@click.argument("depends_on")
def add_cmd(project: str, depends_on: str) -> None:
    """Add DEPENDS_ON as a dependency of PROJECT."""
    try:
        deps = add_dependency(project, depends_on)
        click.echo(f"'{project}' now depends on: {', '.join(deps)}")
    except DependencyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@deps_cmd.command("remove")
@click.argument("project")
@click.argument("depends_on")
def remove_cmd(project: str, depends_on: str) -> None:
    """Remove DEPENDS_ON from PROJECT's dependencies."""
    try:
        deps = remove_dependency(project, depends_on)
        remaining = ", ".join(deps) if deps else "(none)"
        click.echo(f"Removed. '{project}' now depends on: {remaining}")
    except DependencyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@deps_cmd.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List all dependencies of PROJECT."""
    deps = list_dependencies(project)
    if not deps:
        click.echo(f"'{project}' has no dependencies.")
    else:
        for dep in deps:
            click.echo(dep)


@deps_cmd.command("dependents")
@click.argument("project")
def dependents_cmd(project: str) -> None:
    """List all projects that depend on PROJECT."""
    dependents = list_dependents(project)
    if not dependents:
        click.echo(f"No projects depend on '{project}'.")
    else:
        for p in dependents:
            click.echo(p)


@deps_cmd.command("all")
def all_cmd() -> None:
    """Show the full dependency map."""
    data = all_dependencies()
    if not data:
        click.echo("No dependencies recorded.")
        return
    for project, deps in sorted(data.items()):
        click.echo(f"{project}: {', '.join(deps)}")
