# llmsdottxt-mcp

All notable changes to this project are documented here.

## 0.2.0

### Minor Changes

- `browse(package, section)` now slices `llms-full.txt` to the matching H1 page — and lists the available page titles when nothing matches — instead of returning the whole document.
- `search` ranked results and the empty-query package listing now paginate via `limit` and `offset`.
- MCP tool responses are token-trimmed: response models omit null and default-valued fields while keeping the structured-output schema valid.

### Patch Changes

- Fixed a stdio transport crash caused by forwarding `host`/`port` to `mcp.run`.
- Mirrored the llms.txt specification under `docs/references` for offline reference.

## 0.1.1

### Patch Changes

- Add a `Changelog` project URL so PyPI links directly to this changelog.

## 0.1.0

### Minor Changes

- Initial public release. Local-first MCP server that scans a project's dependencies (Python, Node, Rust, Go), discovers each package's `llms.txt` documentation endpoint, fetches and indexes the content locally, and exposes it to AI coding agents over the Model Context Protocol.
