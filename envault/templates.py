"""Template management for envault — save and apply env variable templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.storage import _base_dir


class TemplateError(Exception):
    pass


def _templates_path() -> Path:
    p = _base_dir() / "templates"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _template_file(name: str) -> Path:
    return _templates_path() / f"{name}.json"


def save_template(name: str, keys: Dict[str, str], description: str = "") -> None:
    """Persist a named template with a dict of key→default_value pairs."""
    if not name.strip():
        raise TemplateError("Template name must not be empty.")
    payload = {"name": name, "description": description, "keys": keys}
    _template_file(name).write_text(json.dumps(payload, indent=2))


def load_template(name: str) -> Dict[str, str]:
    """Return the key→default_value mapping for *name*."""
    path = _template_file(name)
    if not path.exists():
        raise TemplateError(f"Template '{name}' not found.")
    data = json.loads(path.read_text())
    return data["keys"]


def list_templates() -> List[Dict]:
    """Return metadata for every saved template (name + description)."""
    result = []
    for f in sorted(_templates_path().glob("*.json")):
        data = json.loads(f.read_text())
        result.append({"name": data["name"], "description": data.get("description", "")})
    return result


def delete_template(name: str) -> None:
    path = _template_file(name)
    if not path.exists():
        raise TemplateError(f"Template '{name}' not found.")
    path.unlink()


def apply_template(name: str, overrides: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Return a ready-to-use env dict from *name*, optionally overriding defaults."""
    env = dict(load_template(name))
    if overrides:
        env.update(overrides)
    return env
