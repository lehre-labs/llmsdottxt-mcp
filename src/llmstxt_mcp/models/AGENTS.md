# Models Package

Typed domain, persisted, and response models. The bottom layer — imports nothing internal.

## Conventions

- Prefer explicit Pydantic models over `dict[str, Any]`.
- Constrained string aliases and enums live in `strings.py`; reuse them at boundaries.
- Use `StrEnum` for finite protocol values and `Literal` (`LogLevel`) for fixed string sets.
- Mutable field defaults use `Field(default_factory=...)`.

## Gotchas

- Pydantic and FastMCP resolve annotations at runtime, so field types must be importable at runtime — `flake8-type-checking` is disabled here on purpose (see `pyproject.toml`).
- Model the tool-facing shape; do not mirror raw registry/API payloads.

## Testing

- Run `uv run ty check` and `uv run basedpyright` after changes.

## Out Of Scope

- HTTP, fetching, registration, business logic.
