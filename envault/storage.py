"""Local encrypted storage for .env file contents."""

import json
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt


STORE_DIR = Path.home() / ".envault" / "store"


def _project_path(project_name: str) -> Path:
    """Return the path to the encrypted store file for a project."""
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    return STORE_DIR / f"{project_name}.enc"


def save_env(project_name: str, env_contents: str, passphrase: str) -> None:
    """Encrypt and persist .env contents for a named project."""
    ciphertext = encrypt(env_contents, passphrase)
    _project_path(project_name).write_bytes(ciphertext)


def load_env(project_name: str, passphrase: str) -> str:
    """Load and decrypt .env contents for a named project."""
    path = _project_path(project_name)
    if not path.exists():
        raise FileNotFoundError(f"No stored env found for project '{project_name}'.")
    return decrypt(path.read_bytes(), passphrase)


def list_projects() -> list[str]:
    """Return names of all projects with stored env files."""
    if not STORE_DIR.exists():
        return []
    return [p.stem for p in STORE_DIR.glob("*.enc")]


def delete_env(project_name: str) -> bool:
    """Delete the stored env for a project. Returns True if deleted, False if not found."""
    path = _project_path(project_name)
    if path.exists():
        path.unlink()
        return True
    return False
