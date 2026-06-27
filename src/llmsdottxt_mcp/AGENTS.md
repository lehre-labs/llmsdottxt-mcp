# llmsdottxt_mcp Package

Source root for the layered server. Read the root [`AGENTS.md`](../../AGENTS.md) and [`CONTEXT-MAP.md`](../../CONTEXT-MAP.md) first.

## Single-module concerns

- `pipeline.py` — the only orchestrator: scanners → resolvers → platforms → fetcher → index.
- `http.py` — shared `AsyncClient` with tenacity retry + aiolimiter rate limiting.
- `fetcher.py` — fetch + parse `llms.txt`, stream + size-cap `llms-full.txt`.
- `index/` — SQLite (FTS5) index split by concern: `_connection` (lifecycle +
  migrations), `_sql` (low-level helpers), `_entries` (CRUD + search), `_meta`,
  `_cache` (gzip full-text). Public API re-exported from `index/__init__.py`.
- `errors.py` — typed error hierarchy converted to `ToolError` at the tool boundary.
- `cli.py` — Typer CLI: `scan`, `serve`, `status`, `doctor`, `clear`.
- `server.py` — FastMCP composition root (`create_server`, `mcp`).

## Rules

- Keep `pipeline` the only place that combines the discovery layer.
- Respect the import contract (`uv run lint-imports`).
- Never `print()`; log JSON to stderr via structlog.
