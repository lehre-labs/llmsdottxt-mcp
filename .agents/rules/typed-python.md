---
name: typed-python
description: Typed boundaries and string aliases.
globs: ["src/llmsdottxt_mcp/models/**/*.py", "src/llmsdottxt_mcp/**/*.py"]
---
- Put constrained string aliases and finite enums in `models/strings.py`.
- Use `StrEnum` for finite protocol values: `Ecosystem`, `Platform`, `DocsUrlSource`.
- Use `LogLevel` (a `Literal`) for log levels.
- Validate tool inputs with aliases (`PackageName`, `SearchQuery`); keep fetched third-party text tolerant.
- Pydantic and FastMCP resolve annotations at runtime — model field types and tool return types must be importable at runtime (not under `TYPE_CHECKING`).
