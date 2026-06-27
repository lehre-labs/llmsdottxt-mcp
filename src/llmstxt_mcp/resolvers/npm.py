"""npm resolver for the Node ecosystem."""

from __future__ import annotations

from typing import ClassVar, override

import httpx
import structlog

from llmstxt_mcp import http
from llmstxt_mcp.models import DocsInfo, DocsUrlSource, Ecosystem
from llmstxt_mcp.resolvers.base import BaseResolver

logger = structlog.get_logger(__name__)


class NpmResolver(BaseResolver):
    """Resolves docs via the npm registry."""

    ecosystem: ClassVar[Ecosystem] = Ecosystem.node

    @override
    async def resolve(self, package: str, client: httpx.AsyncClient) -> DocsInfo | None:
        url = f"https://registry.npmjs.org/{package}/latest"
        try:
            response = await http.get(client, url)
            if response.status_code != 200:
                return None
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("npm_resolve_failed", package=package, error=str(exc))
            return None

        homepage = data.get("homepage")
        repo = data.get("repository")
        repo_url = repo.get("url") if isinstance(repo, dict) else repo

        return DocsInfo(
            package=package,
            ecosystem=Ecosystem.node,
            docs_base_url=homepage.rstrip("/") if homepage else None,
            docs_url_source=DocsUrlSource.homepage_fallback if homepage else DocsUrlSource.none,
            repository_url=_clean_git_url(repo_url),
            original_homepage=homepage,
            latest_version=data.get("version"),
        )


def _clean_git_url(url: str | None) -> str | None:
    """Normalize a git+https://... repository URL to a plain https URL."""
    if not url:
        return None
    return url.removeprefix("git+").removesuffix(".git")
