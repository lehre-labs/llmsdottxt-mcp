# llmsdottxt-mcp

**Auto-discover [`llms.txt`](https://llmstxt.org) from your deps. Docs your agent can read. Zero setup.**

`llmsdottxt-mcp` scans your project's dependencies, discovers each package's `llms.txt` documentation endpoint, fetches and indexes the content locally, and exposes it to AI coding agents over the Model Context Protocol — so your agent reads first-party docs instead of guessing or scraping.

## Why

Unlike scraping-based doc tools, llmsdottxt-mcp is **local-first** and **llms.txt-native**: auto-discovery from your real dependencies, platform-aware fetching (Mintlify, Read the Docs, Docusaurus, GitHub Pages), a persistent searchable index, and size-safe handling of large `llms-full.txt` files.

It is also resilient to docs hosts that push back: a genuine `429`/`503` is retried with backoff (honoring `Retry-After`), while an unsolvable bot challenge — Cloudflare, DataDome, Imperva, AWS WAF, Akamai, Sucuri — is detected and reported as **blocked** (a browser is required to pass it), so it is never silently miscounted as "no docs".

## Status

- Project status: pre-1.0 public preview.
- Python: 3.14+.
- API stability: MCP tool names and response schemas may change before 1.0.
- Support: GitHub issues for bugs and features; private security reports for vulnerabilities.

## Install & Run

```sh
uvx llmsdottxt-mcp scan      # index the current project's dependencies
uvx llmsdottxt-mcp status    # show indexed packages
uvx llmsdottxt-mcp serve     # start the MCP server on stdio
uvx llmsdottxt-mcp doctor    # diagnose paths, write access, registry connectivity
```

Add it to an MCP client (e.g. Claude Code) as a stdio server running `llmsdottxt-mcp serve`.

## MCP Surface

**Tools:** `index_deps`, `search`, `browse`, `status`.
**Resources:** `llmstxt://packages`, `llmstxt://package/{ecosystem}/{name}`.
**Prompts:** `find_docs_for_import`.

## Configuration

Everything is convention-based; override via `LLMSTXT_*` env vars (see [`.env.example`](./.env.example)). The index lives in `~/.llms.txt.d/`.

## Ecosystems

Four ecosystems are supported end-to-end — each pairs a manifest scanner with a registry resolver:

| Ecosystem | Manifest(s) | Registry | Docs source |
| --- | --- | --- | --- |
| Python | `pyproject.toml`, `requirements.txt` | PyPI JSON API | project URLs / homepage |
| Node | `package.json` | npm registry | homepage |
| Rust | `Cargo.toml` | crates.io API | `documentation` / homepage |
| Go | `go.mod` | proxy.golang.org | pkg.go.dev |

Add an ecosystem by dropping a `BaseScanner` and `BaseResolver` into their registries — see [`ROADMAP.md`](./ROADMAP.md).

## Development

```sh
uv sync --all-groups
uv run ruff check && uv run ty check && uv run basedpyright
uv run lint-imports && uv run pytest -n auto
```

See [`AGENTS.md`](./AGENTS.md) for architecture and conventions.
