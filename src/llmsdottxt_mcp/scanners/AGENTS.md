# Scanners Package

Extract direct dependencies from project manifests. Pure parsing — no network.

## Conventions

- Add a scanner by subclassing `BaseScanner` (set `ecosystem`, implement `can_handle` + `extract_deps`) and appending it to `SCANNER_REGISTRY`.
- Return `Dependency` models; skip the runtime/toolchain itself (`python`, `pip`, ...).

## Gotchas

- Python uses stdlib `tomllib` (3.11+); strip extras and version operators from names.

## Out Of Scope

- Resolving docs URLs, fetching, HTTP.
