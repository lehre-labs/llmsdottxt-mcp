"""Resource registration grouped by domain."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmsdottxt_mcp.resources import packages

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_resources(mcp: FastMCP) -> None:
    """Register all MCP resources."""
    packages.register(mcp)
