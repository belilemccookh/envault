"""Secure project sharing via encrypted export bundles."""

from __future__ import annotations

import json
import os
import base64
from pathlib import Path
from typing import Optional

from envault.crypto import derive_key, get_fernet
from envault.storage import load_env, save_env
from envault.audit import record


class ShareError(Exception):
    """Raised when a share/import operation fails."""


def export_bundle(
    project: str,
    passphrase: str,
    share_passphrase: str,
    output_path: Optional[Path] = None,
) -> Path:
    """Export a project's env vars as a self-contained encrypted bundle.

    The bundle is re-encrypted with *share_passphrase* so it can be
    transferred to another user without exposing the master passphrase.
    """
    env = load_env(project, passphrase)
    if env is None:
        raise ShareError(f"Project '{project}' not found or wrong passphrase.")

    payload = json.dumps(env).encode()
    fernet = get_fernet(share_passphrase)
    encrypted = fernet.encrypt(payload)

    bundle = {
        "project": project,
        "data": base64.b64encode(encrypted).decode(),
    }

    if output_path is None:
        output_path = Path(f"{project}.envbundle")

    output_path.write_text(json.dumps(bundle, indent=2))
    record(project, "share_export", success=True)
    return output_path


def import_bundle(
    bundle_path: Path,
    share_passphrase: str,
    dest_passphrase: str,
    project_override: Optional[str] = None,
) -> str:
    """Import an encrypted bundle and store it under the local vault.

    Returns the project name that was saved.
    """
    try:
        bundle = json.loads(bundle_path.read_text())
        project = project_override or bundle["project"]
        encrypted = base64.b64decode(bundle["data"])
    except (KeyError, ValueError, OSError) as exc:
        raise ShareError(f"Invalid bundle file: {exc}") from exc

    fernet = get_fernet(share_passphrase)
    try:
        payload = fernet.decrypt(encrypted)
    except Exception as exc:
        raise ShareError("Failed to decrypt bundle — wrong share passphrase?") from exc

    env: dict[str, str] = json.loads(payload)
    save_env(project, env, dest_passphrase)
    record(project, "share_import", success=True)
    return project
