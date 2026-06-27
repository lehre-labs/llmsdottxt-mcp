# Tools Package

Thin FastMCP tool wrappers. Delegate to `pipeline` and `index`; return response models.

## Conventions

- Keep wrappers thin; write docstrings (agents route on them).
- Validate inputs with model aliases (`PackageName`, `SearchQuery`).
- Convert internal errors to `fastmcp.exceptions.ToolError`.
- Register by domain in `registry.py`.

## Gotchas

- FastMCP builds schemas from signatures + return annotations, so model types must be runtime imports (`flake8-type-checking` disabled here).

## Testing

- Update `tests/test_server.py`; verify the server builds with `create_server()`.

## Out Of Scope

- HTTP, parsing, index storage internals.
