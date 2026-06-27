# Tools Context

FastMCP tool wrapper language.

## Language

**Tool**:
A FastMCP-exposed function (`index_deps`, `search`, `browse`, `status`) that delegates to the pipeline or index and returns a response model.
_Avoid_: handler, endpoint, operation, method

**Tool Registry**:
The `register_tools(mcp)` entry point that calls per-domain `register(mcp)` to attach every tool to the MCP server.
_Avoid_: tool list, tool setup, tool boot
