---
name: python-quality
description: Python quality gates.
globs: ["src/**/*.py", "tests/**/*.py"]
---
- Format and lint: `uv run ruff format` then `uv run ruff check --fix`.
- Type-check with both `uv run ty check` and `uv run basedpyright`.
- Enforce the layered architecture: `uv run lint-imports`.
- No `print()` in library code — stdout is the MCP stdio channel. Logs go to stderr via structlog.
- Avoid `Any`; model data with typed Pydantic models.
