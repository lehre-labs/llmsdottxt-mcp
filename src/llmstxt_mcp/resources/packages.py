"""Read-only ``llmstxt://`` resources exposing the local index as context."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmstxt_mcp import index
from llmstxt_mcp.errors import PackageNotIndexedError
from llmstxt_mcp.models import IndexEntry, PackageSummary

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register documentation resources on the server."""
    mcp.resource("llmstxt://packages")(list_indexed_packages)
    mcp.resource("llmstxt://package/{ecosystem}/{name}")(package_entry)


async def list_indexed_packages() -> list[PackageSummary]:
    """All indexed packages with summary metadata."""
    return await index.summaries()


async def package_entry(ecosystem: str, name: str) -> IndexEntry:
    """The full index record for a single package."""
    entry = await index.find(name, ecosystem)
    if entry is None:
        raise PackageNotIndexedError(name)
    return entry
