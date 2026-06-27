# Typed Python

Read before changing Pydantic models, FastMCP tool signatures, or string aliases.

## Rules

- Put string aliases and enums in `src/llmsdottxt_mcp/models/strings.py`.
- Use `StrEnum` for finite protocol values (`Ecosystem`, `Platform`, `DocsUrlSource`).
- Use the `LogLevel` `Literal` for log levels; plain `str` only when a value has no domain meaning.
- Use `PackageName` / `SearchQuery` / `NonEmptyText` for user-supplied tool inputs.
- Keep fetched third-party text tolerant; avoid `dict[str, Any]` — model it.
- Pydantic and FastMCP need field/return types at runtime; do not move them under `TYPE_CHECKING`.
- Run `uv run ty check`, `uv run basedpyright`, `uv run ruff check`, `uv run pytest -n auto`.

## External Docs

- Pydantic: https://pydantic.dev/llms.txt
- FastMCP: https://gofastmcp.com/llms.txt
