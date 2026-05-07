"""Access Control List (ACL) helpers for envault projects.

Provides role-based access control: owner, editor, viewer.
Roles are stored per-project alongside other metadata.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

ROLES = ("owner", "editor", "viewer")


class ACLError(Exception):
    """Raised for ACL-related errors."""


def _acl_path(storage_dir: Path, project: str) -> Path:
    return storage_dir / project / "acl.json"


def _load(storage_dir: Path, project: str) -> Dict[str, str]:
    path = _acl_path(storage_dir, project)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(storage_dir: Path, project: str, data: Dict[str, str]) -> None:
    path = _acl_path(storage_dir, project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def grant(storage_dir: Path, project: str, user: str, role: str) -> Dict[str, str]:
    """Grant *user* a *role* on *project*. Returns updated ACL."""
    if not user.strip():
        raise ACLError("User name must not be empty.")
    if role not in ROLES:
        raise ACLError(f"Invalid role '{role}'. Choose from: {', '.join(ROLES)}.")
    acl = _load(storage_dir, project)
    acl[user] = role
    _save(storage_dir, project, acl)
    return acl


def revoke(storage_dir: Path, project: str, user: str) -> Dict[str, str]:
    """Remove *user* from the ACL of *project*."""
    acl = _load(storage_dir, project)
    if user not in acl:
        raise ACLError(f"User '{user}' not found in ACL for project '{project}'.")
    del acl[user]
    _save(storage_dir, project, acl)
    return acl


def get_role(storage_dir: Path, project: str, user: str) -> Optional[str]:
    """Return the role of *user* for *project*, or None if not present."""
    return _load(storage_dir, project).get(user)


def list_acl(storage_dir: Path, project: str) -> List[Dict[str, str]]:
    """Return a sorted list of {user, role} dicts for *project*."""
    acl = _load(storage_dir, project)
    return [{"user": u, "role": r} for u, r in sorted(acl.items())]


def check_permission(storage_dir: Path, project: str, user: str, required_role: str) -> bool:
    """Return True if *user* has at least *required_role* on *project*."""
    if required_role not in ROLES:
        raise ACLError(f"Unknown role: {required_role}")
    role = get_role(storage_dir, project, user)
    if role is None:
        return False
    return ROLES.index(role) <= ROLES.index(required_role)
