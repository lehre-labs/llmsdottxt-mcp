"""Resolver registry: one resolver per ecosystem."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmstxt_mcp.resolvers.crates import CratesResolver
from llmstxt_mcp.resolvers.go import GoResolver
from llmstxt_mcp.resolvers.npm import NpmResolver
from llmstxt_mcp.resolvers.pypi import PyPIResolver

if TYPE_CHECKING:
    from llmstxt_mcp.models import Ecosystem
    from llmstxt_mcp.resolvers.base import BaseResolver

RESOLVER_REGISTRY: list[type[BaseResolver]] = [
    PyPIResolver,
    NpmResolver,
    CratesResolver,
    GoResolver,
]


def get_resolver(ecosystem: Ecosystem) -> BaseResolver | None:
    """Return a resolver instance for the ecosystem, or None if unsupported."""
    for resolver_cls in RESOLVER_REGISTRY:
        if resolver_cls.ecosystem == ecosystem:
            return resolver_cls()
    return None
