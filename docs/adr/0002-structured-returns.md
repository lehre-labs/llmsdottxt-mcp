# Structured Pydantic tool returns over strings

The initial plan returned markdown strings from tools. We switched to typed Pydantic models (`ScanReport`, `PackageSummary`, `SearchHit`, `StatusReport`) because agents parse structured content more reliably, while `resolve_docs` returns raw text by necessity. FastMCP emits JSON schemas + structured content.

## Consequences

Reliable agent parsing and validation. Model field/return types must be runtime-importable — `flake8-type-checking` is disabled for model and FastMCP-boundary modules.
