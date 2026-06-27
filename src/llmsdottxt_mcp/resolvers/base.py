"""Base resolver interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    import httpx

    from llmsdottxt_mcp.models import DocsInfo, Ecosystem


class BaseResolver(ABC):
    """Maps a package name to its documentation location for one ecosystem."""

    ecosystem: ClassVar[Ecosystem]

    @abstractmethod
    async def resolve(self, package: str, client: httpx.AsyncClient) -> DocsInfo | None:
        """Resolve a package to a DocsInfo, or None if no docs URL is found."""
