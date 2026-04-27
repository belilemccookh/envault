"""Export and import utilities for envault projects."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from envault.crypto import decrypt, encrypt, get_fernet
from envault.storage import load_env, save_env


def export_env(project: str, passphrase: str, output_path: str) -> None:
    """Export a project's env vars to an encrypted JSON bundle file."""
    env_vars = load_env(project, passphrase)
    if env_vars is None:
        raise KeyError(f"Project '{project}' not found.")

    bundle = json.dumps({"project": project, "vars": env_vars}).encode()
    fernet = get_fernet(passphrase)
    encrypted_bundle = fernet.encrypt(bundle)

    dest = Path(output_path)
    dest.write_bytes(encrypted_bundle)


def import_env(
    input_path: str,
    passphrase: str,
    project_override: str | None = None,
    overwrite: bool = False,
) -> str:
    """Import an encrypted bundle file into envault storage.

    Returns the project name that was imported.
    """
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"Bundle file not found: {input_path}")

    encrypted_bundle = src.read_bytes()
    fernet = get_fernet(passphrase)

    try:
        raw = fernet.decrypt(encrypted_bundle)
    except Exception as exc:
        raise ValueError("Failed to decrypt bundle — wrong passphrase?") from exc

    data = json.loads(raw.decode())
    project = project_override or data["project"]
    env_vars: Dict[str, str] = data["vars"]

    existing = load_env(project, passphrase)
    if existing is not None and not overwrite:
        raise FileExistsError(
            f"Project '{project}' already exists. Use overwrite=True to replace."
        )

    merged = {**(existing or {}), **env_vars} if not overwrite else env_vars
    save_env(project, merged, passphrase)
    return project


def env_to_dotenv(env_vars: Dict[str, str]) -> str:
    """Serialize a dict of env vars to .env file format string."""
    lines = []
    for key, value in sorted(env_vars.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + "\n" if lines else ""


def dotenv_to_dict(content: str) -> Dict[str, str]:
    """Parse a .env file content string into a dict."""
    result: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result
