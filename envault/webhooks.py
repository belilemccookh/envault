"""Webhook notifications for envault events."""
from __future__ import annotations

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from envault.storage import _project_path


class WebhookError(Exception):
    """Raised when a webhook operation fails."""


def _webhooks_path(base_dir: Path | None = None) -> Path:
    root = base_dir or _project_path("").parent
    return root / "_webhooks.json"


def _load(base_dir: Path | None = None) -> dict[str, list[str]]:
    path = _webhooks_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(data: dict[str, list[str]], base_dir: Path | None = None) -> None:
    _webhooks_path(base_dir).write_text(json.dumps(data, indent=2))


def register(project: str, url: str, base_dir: Path | None = None) -> None:
    """Register a webhook URL for a project."""
    if not url.startswith(("http://", "https://")):
        raise WebhookError(f"Invalid URL scheme: {url}")
    data = _load(base_dir)
    hooks = data.setdefault(project, [])
    if url not in hooks:
        hooks.append(url)
    _save(data, base_dir)


def unregister(project: str, url: str, base_dir: Path | None = None) -> bool:
    """Remove a webhook URL. Returns True if it was present."""
    data = _load(base_dir)
    hooks = data.get(project, [])
    if url not in hooks:
        return False
    hooks.remove(url)
    if not hooks:
        data.pop(project, None)
    _save(data, base_dir)
    return True


def list_hooks(project: str, base_dir: Path | None = None) -> list[str]:
    """Return all registered webhook URLs for a project."""
    return list(_load(base_dir).get(project, []))


def notify(
    project: str,
    event: str,
    payload: dict[str, Any] | None = None,
    base_dir: Path | None = None,
) -> list[tuple[str, bool, str]]:
    """POST event payload to all registered hooks. Returns (url, ok, msg) list."""
    body = json.dumps({"project": project, "event": event, **(payload or {})}).encode()
    results: list[tuple[str, bool, str]] = []
    for url in list_hooks(project, base_dir):
        try:
            req = urllib.request.Request(
                url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                results.append((url, True, str(resp.status)))
        except urllib.error.URLError as exc:
            results.append((url, False, str(exc.reason)))
        except Exception as exc:  # noqa: BLE001
            results.append((url, False, str(exc)))
    return results
