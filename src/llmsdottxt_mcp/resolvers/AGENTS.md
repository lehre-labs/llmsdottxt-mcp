# Resolvers Package

Map a dependency to its documentation URL via package registries.

## Conventions

- Add an ecosystem: subclass `BaseResolver` (set `ecosystem`, implement `async resolve`) and register it in `RESOLVER_REGISTRY`. One resolver per Ecosystem.
- Request through `llmsdottxt_mcp.http.get`; tolerate failures by returning `None` and logging.

## Gotchas

- Registry JSON shapes differ (PyPI `project_urls`, npm `repository.url`, crates `crate.documentation`).

## Out Of Scope

- Platform detection, fetching llms.txt, indexing.
