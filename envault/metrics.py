"""Project metrics: key counts, last-modified timestamps, and usage stats."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from envault.storage import _project_path, list_projects, load_env


@dataclass
class ProjectMetrics:
    project: str
    key_count: int
    size_bytes: int
    last_modified: Optional[str]  # ISO-8601 or None
    keys: List[str] = field(default_factory=list)


class MetricsError(Exception):
    pass


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def project_metrics(project: str, passphrase: str) -> ProjectMetrics:
    """Return metrics for a single project."""
    if not project:
        raise MetricsError("project name must not be empty")

    env_path = _project_path(project)
    if not env_path.exists():
        raise MetricsError(f"project '{project}' not found")

    stat = env_path.stat()
    size_bytes = stat.st_size
    last_modified = _iso(stat.st_mtime)

    data = load_env(project, passphrase)
    keys = sorted(data.keys())

    return ProjectMetrics(
        project=project,
        key_count=len(keys),
        size_bytes=size_bytes,
        last_modified=last_modified,
        keys=keys,
    )


def all_metrics(passphrase: str) -> List[ProjectMetrics]:
    """Return metrics for every stored project."""
    results: List[ProjectMetrics] = []
    for name in list_projects():
        try:
            results.append(project_metrics(name, passphrase))
        except MetricsError:
            continue
    return sorted(results, key=lambda m: m.project)


def summary(metrics: List[ProjectMetrics]) -> Dict[str, int]:
    """Aggregate totals across a list of ProjectMetrics."""
    return {
        "total_projects": len(metrics),
        "total_keys": sum(m.key_count for m in metrics),
        "total_bytes": sum(m.size_bytes for m in metrics),
    }
