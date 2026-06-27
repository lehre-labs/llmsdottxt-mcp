# Config Package

Settings, constants, and logging. Imports only `models` (for `LogLevel`).

## Conventions

- All runtime knobs are `LLMSTXT_*` env vars with sane defaults; keep them in `Settings`.
- Derive paths from `index_root` via properties — never hardcode `~/.llms.txt.d` elsewhere.
- `configure_logging` writes JSON to **stderr**; stdout is the MCP channel.

## Gotchas

- `settings` is a module-level singleton; tests override `settings.index_root` via monkeypatch.

## Out Of Scope

- HTTP, fetching, business logic.
