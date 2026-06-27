# Agent Documentation Guide

Agent-facing docs for `llmstxt-mcp`. Keep them compact, source-linked, and optimized for coding agents that need enough context to make correct changes without loading the whole internet.

## Source Order

1. Root `AGENTS.md` for project-wide rules.
2. `CONTEXT-MAP.md` to find the relevant context file.
3. Package-local `AGENTS.md` and `CONTEXT.md` when editing a package that has them.
4. `pyproject.toml`, `.python-version`, `.env.example` for runtime and tool facts.
5. Local source before changing behavior.
6. [`source-map.md`](./source-map.md) when a dependency's behavior may have changed.

## Documentation Shape

- `docs/agents/`: routing, invariants, source maps, machine-friendly notes.
- `docs/human/`: human guides and narrative docs.

Pick one type per page: tutorial, how-to, reference, or explanation.

## Writing Rules

- Keep titles literal; use canonical terms from the relevant `CONTEXT.md`.
- Link to official docs instead of copying them; record source URLs on the page that depends on them.
- Date only volatile claims (current library behavior, tested endpoints).
- Document the code that exists or an accepted decision — not speculative architecture.

## Project Checks

```sh
uv run ruff format --check && uv run ruff check
uv run ty check && uv run basedpyright
uv run lint-imports
uv run bandit -q -c pyproject.toml -r src
uv run pytest -n auto
```
