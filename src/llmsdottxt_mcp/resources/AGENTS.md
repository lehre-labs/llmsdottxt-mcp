# Resources Package

Read-only `llmstxt://` context resources backed by the index. No side effects.

## Conventions

- Resources read from `index` and return models; never fetch or mutate.
- Register URIs in `registry.py`.

## Gotchas

- Resource return annotations are evaluated at runtime by FastMCP -- keep model imports runtime.

## Out Of Scope

- Scanning, fetching, write actions (those are tools).
