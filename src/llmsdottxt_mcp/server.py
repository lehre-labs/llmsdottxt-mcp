"""FastMCP server composition root."""

from __future__ import annotations

from fastmcp import FastMCP

from llmsdottxt_mcp.config import DEFAULT_MCP_HOST, DEFAULT_MCP_PORT
from llmsdottxt_mcp.models import Transport
from llmsdottxt_mcp.prompts import register_prompts
from llmsdottxt_mcp.resources import register_resources
from llmsdottxt_mcp.tools import register_tools

INSTRUCTIONS = (
    "Auto-discover llms.txt from your deps. Docs your agent can read. Zero setup."
    "Run index_deps to scan the current project's dependencies, then use search "
    "to list or find packages and browse to read their documentation (TOC or full-text). "
    "Read-only context is available through llmstxt:// resources. "
    "The index is shared across projects and persists on disk."
)


def create_server() -> FastMCP:
    """Create a fully registered llmsdottxt-mcp server."""
    server = FastMCP("llmsdottxt-mcp", instructions=INSTRUCTIONS)
    register_tools(server)
    register_resources(server)
    register_prompts(server)
    return server


mcp = create_server()


def serve(
    transport: Transport = Transport.stdio,
    host: str = DEFAULT_MCP_HOST,
    port: int = DEFAULT_MCP_PORT,
) -> None:
    """Run the MCP server with the chosen transport."""
    if transport is Transport.stdio:
        # stdio's transport runner takes no host/port -- forwarding them raises TypeError.
        mcp.run(transport="stdio")
    else:
        mcp.run(transport=transport.to_fastmcp(), host=host, port=port)


def main() -> None:
    """Run the MCP server over stdio transport."""
    mcp.run()


if __name__ == "__main__":
    main()
