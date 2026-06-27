# Contributing

Thanks for improving `llmsdottxt-mcp`. Keep changes focused, typed, and safe: this tool fetches third-party documentation, so treat all fetched content as untrusted.

## Setup

```sh
uv sync --all-groups
cp .env.example .env
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

## Local Checks

```sh
uv run ruff format --check
uv run ruff check
uv run ty check
uv run basedpyright
uv run lint-imports
uv run deptry .
uv run bandit -q -c pyproject.toml -r src
uv run pip-audit
uv run pytest -n auto
```

## Releases

See [`docs/release-checklist.md`](./docs/release-checklist.md).

## Rules

- Read [`AGENTS.md`](./AGENTS.md) first — it encodes the layered architecture, domain language, and observability rules.
- Imports flow downward only; verify with `uv run lint-imports`.
- Never `print()` in library code — stdout is the MCP stdio channel.
- Treat fetched `llms.txt` as untrusted; never commit the `~/.llms.txt.d/` cache.
- Write a test for every new function or bug fix; reproduce bugs before fixing them.
- Use Conventional Commits.
