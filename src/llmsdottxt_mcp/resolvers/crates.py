"""crates.io resolver for the Rust ecosystem."""

from __future__ import annotations

from typing import ClassVar, override

import httpx
import structlog

from llmsdottxt_mcp import http
from llmsdottxt_mcp.models import DocsInfo, DocsUrlSource, Ecosystem
from llmsdottxt_mcp.resolvers.base import BaseResolver

logger = structlog.get_logger(__name__)


class CratesResolver(BaseResolver):
    """Resolves docs via the crates.io API."""

    ecosystem: ClassVar[Ecosystem] = Ecosystem.rust

    @override
    async def resolve(self, package: str, client: httpx.AsyncClient) -> DocsInfo | None:
        url = f"https://crates.io/api/v1/crates/{package}"
        try:
            response = await http.get(client, url)
            if response.status_code != 200:
                return None
            crate = response.json().get("crate", {})
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("crates_resolve_failed", package=package, error=str(exc))
            return None

        docs_url = crate.get("documentation") or crate.get("homepage")

        return DocsInfo(
            package=package,
            ecosystem=Ecosystem.rust,
            docs_base_url=docs_url.rstrip("/") if docs_url else None,
            docs_url_source=DocsUrlSource.registry_documentation
            if docs_url
            else DocsUrlSource.none,
            repository_url=crate.get("repository"),
            original_homepage=crate.get("homepage"),
            latest_version=crate.get("max_stable_version") or crate.get("newest_version"),
        )
