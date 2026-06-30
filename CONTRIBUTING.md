# Contributing

Thanks for improving `llmsdottxt-mcp`. Keep changes focused, typed, and safe: this tool fetches third-party documentation, so treat all fetched content as untrusted.

## Setup

This repo vendors agent tooling (skills, hooks, MCP config) as a git submodule at `.xebec`. Clone with `--recurse-submodules`, or run `git submodule update --init` in an existing clone -- otherwise the `.claude/skills` and `.claude/hooks` symlinks dangle. The submodule is agent-tooling only; it is not needed to build, test, or run `llmsdottxt-mcp`.

```sh
git clone --recurse-submodules https://github.com/lehre-labs/llmsdottxt-mcp.git
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

- Read [`AGENTS.md`](./AGENTS.md) first -- it points to the engineering rules, domain language, and observability constraints.
- Imports flow downward only; verify with `uv run lint-imports`.
- Never `print()` in library code -- stdout is the MCP stdio channel.
- Treat fetched `llms.txt` as untrusted; never commit the `~/.llms.txt.d/` cache.
- Write a test for every new function or bug fix; reproduce bugs before fixing them.
- Use Conventional Commits.
