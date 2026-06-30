# Index Package

SQLite (FTS5) documentation index at `~/.llms.txt.d/index.db`. The public API is re-exported from `__init__.py`; callers never import submodules directly.

## Conventions

- Split concerns: `_connection` (lifecycle + migrations), `_sql` (low-level helpers), `_entries` (CRUD + search), `_meta` (metadata), `_cache` (gzip full-text).
- Every `_sql` helper takes an already-open connection and binds user values via `?` placeholders. Only the fixed `_ENTRY_COLS` constant is interpolated.
- Single async connection per process (WAL mode). Connection is created lazily via `_get_conn()` -- no manual open/close.
- FTS5 trigger logic lives in `_insert_entry`; always delete-then-insert FTS rows to stay consistent with the main table.

## Gotchas

- `_connection` globals (`_conn`, `_init_lock`) are forwarded through `__init__.py.__getattr__` so tests and CLI can observe them without importing the submodule.
- `_cache` is synchronous (gzip I/O); it runs in the main thread and is fast enough that `run_in_executor` isn't needed.
- The legacy JSON import in `_connection._maybe_import_json` is one-shot -- it runs on first connect and never again.

## Testing

- Tests live in `tests/test_index.py` and use a temporary SQLite file per test.
- `close()` resets the connection globals so tests can open fresh connections.

## Out Of Scope

- Pipeline orchestration, HTTP fetching, docs parsing -- those are upstream concerns.
- The `search()` function returns `SearchHit` models with ranked snippets; the consumer decides how to display them.
