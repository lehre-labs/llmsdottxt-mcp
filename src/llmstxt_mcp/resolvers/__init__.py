"""Package-registry resolvers: map a dependency to its documentation URL.

Add a new ecosystem by dropping a ``BaseResolver`` subclass in this package and
registering it in ``registry.RESOLVER_REGISTRY``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmstxt_mcp.resolvers.base import BaseResolver
from llmstxt_mcp.resolvers.registry import RESOLVER_REGISTRY, get_resolver

if TYPE_CHECKING:
    import httpx

    from llmstxt_mcp.models import DocsInfo, Ecosystem


async def resolve(package: str, ecosystem: Ecosystem, client: httpx.AsyncClient) -> DocsInfo | None:
    """Resolve a package to its documentation location for its ecosystem."""
    resolver = get_resolver(ecosystem)
    if resolver is None:
        return None
    return await resolver.resolve(package, client)


__all__ = ["RESOLVER_REGISTRY", "BaseResolver", "get_resolver", "resolve"]
