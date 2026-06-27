"""Go resolver: pkg.go.dev docs via the module proxy."""

from __future__ import annotations

import re
from typing import ClassVar, override

import httpx
import structlog

from llmsdottxt_mcp import http
from llmsdottxt_mcp.config.constants import GO_FORGE_HOSTS
from llmsdottxt_mcp.models import DocsInfo, DocsUrlSource, Ecosystem
from llmsdottxt_mcp.resolvers.base import BaseResolver

logger = structlog.get_logger(__name__)

_MAJOR_SUFFIX = re.compile(r"/v\d+$")


class GoResolver(BaseResolver):
    """Resolves docs via pkg.go.dev, confirming the module on proxy.golang.org."""

    ecosystem: ClassVar[Ecosystem] = Ecosystem.go

    @override
    async def resolve(self, package: str, client: httpx.AsyncClient) -> DocsInfo | None:
        url = f"https://proxy.golang.org/{_escape_module(package)}/@latest"
        try:
            response = await http.get(client, url)
            if response.status_code != 200:
                return None
            version = response.json().get("Version")
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("go_resolve_failed", package=package, error=str(exc))
            return None

        return DocsInfo(
            package=package,
            ecosystem=Ecosystem.go,
            docs_base_url=f"https://pkg.go.dev/{package}",
            docs_url_source=DocsUrlSource.registry_documentation,
            repository_url=_repo_url(package),
            latest_version=version,
        )


def _escape_module(module: str) -> str:
    """Case-encode a module path for the proxy (uppercase X -> ``!x``)."""
    return re.sub(r"[A-Z]", lambda m: "!" + m.group().lower(), module)


def _repo_url(module: str) -> str | None:
    """Derive an https repo URL when the module path is hosted on a known forge."""
    path = _MAJOR_SUFFIX.sub("", module)
    parts = path.split("/")
    if len(parts) >= 3 and parts[0] in GO_FORGE_HOSTS:
        return f"https://{'/'.join(parts[:3])}"
    return None
