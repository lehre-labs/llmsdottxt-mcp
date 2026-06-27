"""PyPI resolver for the Python ecosystem."""

from __future__ import annotations

from typing import ClassVar, override

import httpx
import structlog

from llmsdottxt_mcp import http
from llmsdottxt_mcp.models import DocsInfo, DocsUrlSource, Ecosystem
from llmsdottxt_mcp.resolvers.base import BaseResolver

logger = structlog.get_logger(__name__)

_DOCS_KEYS = (
    "documentation",
    "docs",
    "documentation_url",
    "doc_url",
    "readthedocs",
    "read the docs",
    "wiki",
    "manual",
    "guide",
)
_REPO_KEYS = (
    "source",
    "repository",
    "code",
    "github",
    "gitlab",
    "source code",
    "repo",
    "source_code",
)


class PyPIResolver(BaseResolver):
    """Resolves docs via the PyPI JSON API."""

    ecosystem: ClassVar[Ecosystem] = Ecosystem.python

    @override
    async def resolve(self, package: str, client: httpx.AsyncClient) -> DocsInfo | None:
        url = f"https://pypi.org/pypi/{package}/json"
        try:
            response = await http.get(client, url)
            if response.status_code != 200:
                return None
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("pypi_resolve_failed", package=package, error=str(exc))
            return None

        info = data.get("info", {})
        project_urls = info.get("project_urls") or {}
        homepage = info.get("home_page")

        docs_url = _pick(project_urls, (*_DOCS_KEYS, "homepage", "home_page"))
        source = DocsUrlSource.pypi_project_urls
        if not docs_url and homepage:
            docs_url, source = homepage.rstrip("/"), DocsUrlSource.homepage_fallback
        if not docs_url:
            source = DocsUrlSource.none

        return DocsInfo(
            package=package,
            ecosystem=Ecosystem.python,
            docs_base_url=docs_url,
            docs_url_source=source,
            repository_url=_pick(project_urls, _REPO_KEYS, strip=False),
            original_homepage=homepage,
            latest_version=info.get("version"),
        )


def _pick(urls: dict[str, str], keys: tuple[str, ...], *, strip: bool = True) -> str | None:
    """Return the first present URL (case-insensitive key match)."""
    lower = {k.lower(): v for k, v in urls.items() if v}
    for key in keys:
        if key in lower:
            return lower[key].rstrip("/") if strip else lower[key]
    return None
