"""Reusable documentation-workflow prompts."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register documentation prompts on the server."""
    mcp.prompt(find_docs_for_import)


def find_docs_for_import(symbol: str) -> str:
    """Guide an agent to locate documentation for an unfamiliar import or symbol.

    Args:
        symbol: The import path or symbol the user is unsure about (e.g. 'httpx.AsyncClient').
    """
    package = symbol.split(".", maxsplit=1)[0]
    return (
        f"The user needs documentation for `{symbol}`.\n\n"
        f"1. Call `search` with query '{package}' to check the local index.\n"
        f"2. If there is no hit, call `index_deps` to index the current project's dependencies, "
        f"then search again.\n"
        f"3. Use `browse(package='{package}')` to see the TOC; call "
        f"`browse(package='{package}', section='...')` for full-text of a specific section.\n"
        f"4. Cite the docs_base_url from the matching result in your answer."
    )
