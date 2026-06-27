# SQLite index with FTS5 over file-per-package JSON

Status: accepted

ADR 0003 chose one JSON file per package under `~/.llms.txt.d/index/{ecosystem}/{name}.json` — zero dependencies, human-inspectable. Now that all four ecosystems ship working scanners and resolvers, the JSON approach has three limitations: (a) `search()` re-reads and re-parses every file on every call via `list_all()`; (b) two concurrent `scan` invocations racing on the same package can corrupt a file because `add()` calls `write_text()` with no locking; (c) planned features — per-page chunking, section-level full-text retrieval, FTS5-backed search — need structured querying that a file system cannot provide.

We chose a single SQLite file at `~/.llms.txt.d/index.db` using `aiosqlite` (async stdlib wrapper) with WAL mode enabled. FTS5 virtual tables replace substring-scoring for search. One async connection per process, no pool. Schema managed via embedded DDL with a `_meta` table for migration tracking and `IF NOT EXISTS` idempotent migrations — no Alembic.

## Consequences

Concurrent reads + single writer works correctly via WAL mode. `search()` gets real free-text ranking. The index can grow structured data (sections, pages, chunks) without file-count explosion. The trade-off: the index is no longer human-inspectable as individual `.json` files, and `aiosqlite` adds one dependency.

Related: ADR 0003 (superseded by this decision).
