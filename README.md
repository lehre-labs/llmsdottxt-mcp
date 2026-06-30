# llmsdottxt-mcp

> `llms.txt` will be how agents read docs -- so serve it to them natively, from the deps a project already has.

**Auto-discover [`llms.txt`](https://llmstxt.org) from your deps. Docs your agent can read. Zero setup.**

An MCP server that scans your project's dependency manifests, discovers each package's `llms.txt` documentation endpoint, indexes the content locally under `~/.llms.txt.d/`, and serves it to AI coding agents over the Model Context Protocol.

## Quickstart

```sh
uvx llmsdottxt-mcp scan      # index the current project's dependencies
uvx llmsdottxt-mcp status    # show indexed packages
uvx llmsdottxt-mcp serve     # start the MCP server on stdio
uvx llmsdottxt-mcp doctor    # diagnose paths, write access, registry connectivity
```

Add it to an MCP client (e.g. Claude Code) as a stdio server running `llmsdottxt-mcp serve`. Four ecosystems work end-to-end: Python (`pyproject.toml`, `requirements.txt`), Node (`package.json`), Rust (`Cargo.toml`), and Go (`go.mod`).

## Known Limitations

- Pre-1.0: MCP tool names and response schemas may change.
- A package with no discoverable `llms.txt` is a miss -- there is no HTML-scraping fallback.
- Docs hosts behind an unsolvable bot challenge (Cloudflare, DataDome, Imperva, AWS WAF, Akamai, Sucuri) are reported as **blocked**, not indexed -- passing them needs a real browser.
- Python 3.14+ only.
