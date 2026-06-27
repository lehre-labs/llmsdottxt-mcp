"""Prompt registration grouped by domain."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmstxt_mcp.prompts import docs

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all MCP prompts."""
    docs.register(mcp)
