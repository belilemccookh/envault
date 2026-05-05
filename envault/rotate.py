"""Key rotation support for envault.

Allows re-encrypting all stored environments under a new passphrase
without losing any data. Useful when a master passphrase is compromised
or needs to be changed as part of a security policy.
"""

from __future__ import annotations

from typing import Optional

from envault.crypto import get_fernet
from envault.storage import _project_path, list_projects, load_env, save_env


class RotationError(Exception):
    """Raised when key rotation fails for one or more projects."""


def rotate_project(
    project: str,
    old_passphrase: str,
    new_passphrase: str,
) -> None:
    """Re-encrypt a single project's stored environment under a new passphrase.

    Args:
        project: The project name whose env data will be rotated.
        old_passphrase: The current passphrase used to decrypt existing data.
        new_passphrase: The new passphrase to use for re-encryption.

    Raises:
        KeyError: If the project does not exist in storage.
        cryptography.fernet.InvalidToken: If the old passphrase is incorrect.
    """
    # Decrypt with the old key
    env_data = load_env(project, old_passphrase)

    # Re-encrypt with the new key
    save_env(project, env_data, new_passphrase)


def rotate_all(
    old_passphrase: str,
    new_passphrase: str,
    *,
    stop_on_error: bool = False,
) -> dict[str, Optional[Exception]]:
    """Re-encrypt every stored project under a new passphrase.

    Iterates over all known projects and attempts to rotate each one.
    By default, failures are collected and returned rather than stopping
    the entire operation so that a partial rotation can be diagnosed.

    Args:
        old_passphrase: The current passphrase used to decrypt existing data.
        new_passphrase: The new passphrase to use for re-encryption.
        stop_on_error: If True, raise immediately on the first failure.

    Returns:
        A mapping of project name -> Exception (or None on success).

    Raises:
        RotationError: If ``stop_on_error`` is True and any project fails.
    """
    projects = list_projects()
    results: dict[str, Optional[Exception]] = {}

    for project in projects:
        try:
            rotate_project(project, old_passphrase, new_passphrase)
            results[project] = None
        except Exception as exc:  # noqa: BLE001
            if stop_on_error:
                raise RotationError(
                    f"Rotation failed for project '{project}': {exc}"
                ) from exc
            results[project] = exc

    return results


def rotation_summary(results: dict[str, Optional[Exception]]) -> str:
    """Format a human-readable summary of a rotate_all() result.

    Args:
        results: The mapping returned by :func:`rotate_all`.

    Returns:
        A multi-line string suitable for printing to the terminal.
    """
    successes = [p for p, err in results.items() if err is None]
    failures = {p: err for p, err in results.items() if err is not None}

    lines: list[str] = []
    lines.append(f"Rotation complete: {len(successes)} succeeded, {len(failures)} failed.")

    if successes:
        lines.append("  Succeeded:")
        for project in successes:
            lines.append(f"    - {project}")

    if failures:
        lines.append("  Failed:")
        for project, err in failures.items():
            lines.append(f"    - {project}: {err}")

    return "\n".join(lines)
