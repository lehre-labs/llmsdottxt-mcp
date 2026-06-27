"""Tool registration grouped by domain."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmstxt_mcp.tools import docs

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """Register all MCP tools."""
    docs.register(mcp)
