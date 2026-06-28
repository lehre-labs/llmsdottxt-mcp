# Roadmap

Pre-1.0. Direction, not a commitment.

## Done (v0.1)

- [x] Python scanner (pyproject.toml + requirements.txt) with PyPI resolver
- [x] NPM scanner (package.json) with npm registry resolver
- [x] Rust scanner (Cargo.toml) with crates.io resolver
- [x] Go scanner (go.mod) with proxy.golang.org resolver
- [x] 8 platform detectors (Mintlify, ReadTheDocs, ReadMe, Docusaurus, GitBook, Redocly, MkDocs, GitHub Pages)
- [x] llms.txt fetching with host-root fallback, HTML impostor detection, gzip full-text cache
- [x] HTTP client with retry + backoff, WAF/bot-wall detection (Cloudflare, DataDome, Imperva, etc.)
- [x] FastMCP tools: `index_deps`, `search`, `browse`, `status`
- [x] CLI: `scan`, `serve`, `status`, `doctor`, `clear`
- [x] Scanners skip standard library / runtime names per ecosystem
- [x] Poetry dependency group support in Python scanner
- [x] Go `// indirect` comment filtering in go.mod scanner
- [x] Workspace dependency parsing in Cargo.toml scanner
- [x] Refactored hardcoded path strings to `config/constants.py`
- [x] Markdown section parsing via `markdown-it-py`, replacing regex-based parser (H1-H6, code-block aware)
- [x] SQLite index with FTS5, replacing per-package JSON files (ADR 0004)
- [x] Tool surface refactor: `index_deps`, `search`, `browse`, `status` with hint/fallthrough system (ADR 0005)
- [x] HTTP/SSE transport support in `serve` command (ADR 0007)

## Done (v0.2)

- [x] `browse(package, section)` slices llms-full.txt to the matching H1 page instead of returning the whole document, listing available page titles on a miss
- [x] Pagination (`limit`/`offset`) on `search` ranked results and the empty-query package listing
- [x] Token-trimmed MCP responses — response models omit null/default fields while keeping the output schema valid (ADR 0008)

## Now

_Nothing in flight._

## Next

- [ ] Per-page `.md` fetching via `PlatformHint.per_page_md_pattern` with `browse(package, page="/path")`
- [ ] Store llms-full.txt as heading-keyed chunks in SQLite so page retrieval never truncates large documents

## Non-goals

- [ ] Scraping non-`llms.txt` sites
- [ ] Hosting or proxying third-party docs
