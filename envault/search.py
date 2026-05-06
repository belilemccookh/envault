"""Search across stored projects for keys or values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envault.storage import list_projects, load_env


@dataclass
class SearchMatch:
    project: str
    key: str
    value: str


@dataclass
class SearchResult:
    query: str
    matches: list[SearchMatch] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return len(self.matches) > 0

    def by_project(self) -> dict[str, list[SearchMatch]]:
        grouped: dict[str, list[SearchMatch]] = {}
        for m in self.matches:
            grouped.setdefault(m.project, []).append(m)
        return grouped


def search_keys(
    passphrase: str,
    query: str,
    *,
    project: Optional[str] = None,
    case_sensitive: bool = False,
) -> SearchResult:
    """Search all (or a specific) project for keys matching *query*."""
    result = SearchResult(query=query)
    needle = query if case_sensitive else query.lower()

    projects = [project] if project else list_projects()
    for proj in projects:
        try:
            env = load_env(proj, passphrase)
        except Exception:
            continue
        for key, value in env.items():
            haystack = key if case_sensitive else key.lower()
            if needle in haystack:
                result.matches.append(SearchMatch(project=proj, key=key, value=value))
    return result


def search_values(
    passphrase: str,
    query: str,
    *,
    project: Optional[str] = None,
    case_sensitive: bool = False,
) -> SearchResult:
    """Search all (or a specific) project for values matching *query*."""
    result = SearchResult(query=query)
    needle = query if case_sensitive else query.lower()

    projects = [project] if project else list_projects()
    for proj in projects:
        try:
            env = load_env(proj, passphrase)
        except Exception:
            continue
        for key, value in env.items():
            haystack = value if case_sensitive else value.lower()
            if needle in haystack:
                result.matches.append(SearchMatch(project=proj, key=key, value=value))
    return result
