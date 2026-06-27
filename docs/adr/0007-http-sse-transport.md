# HTTP/SSE as a first-class transport alongside stdio

Status: accepted

FastMCP 3.x ships with stdio, SSE, and streamable HTTP transports built in. Our `serve` command currently hardcodes stdio only. This limits the server to local IDE agents — remote scenarios (team-shared index, containerized dev, browser-hosted MCP clients) need an HTTP endpoint.

We chose to add optional HTTP/SSE transport behind a `--transport` flag on the `serve` command (`stdio` default, `sse` for Server-Sent Events, `http` for streamable HTTP). Listen address defaults to `127.0.0.1` for safety. No auth layer at launch — the trust model matches stdio (local-only). FastMCP's built-in header auth is available if remote binding is ever needed.

## Consequences

One-line change in `serve()`. Same tool surface, same index, just a different pipe. The trade-off: HTTP/SSE exposes the server on a port, which means we must document the default listen address and consider future auth requirements.
