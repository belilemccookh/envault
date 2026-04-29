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


def project_exists(project_name: str) -> bool:
    """Return True if a stored env file exists for the given project name."""
    return (STORE_DIR / f"{project_name}.enc").exists()


def rename_project(old_name: str, new_name: str) -> None:
    """Rename a stored project env file.

    Raises FileNotFoundError if the source project does not exist.
    Raises FileExistsError if a project with the new name already exists.
    """
    old_path = _project_path(old_name)
    if not old_path.exists():
        raise FileNotFoundError(f"No stored env found for project '{old_name}'.")
    new_path = _project_path(new_name)
    if new_path.exists():
        raise FileExistsError(f"A stored env already exists for project '{new_name}'.")
    old_path.rename(new_path)
