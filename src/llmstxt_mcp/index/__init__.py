"""SQLite-backed documentation index: FTS5 search + gzip full-text cache.

The public API is re-exported here; submodules split the concerns:

- ``_connection`` — connection lifecycle, migrations, legacy JSON import
- ``_sql`` — low-level, connection-parameterized SQL helpers
- ``_entries`` — entry CRUD, ranked search, summaries, ``clear_all``
- ``_meta`` — index metadata persistence
- ``_cache`` — gzip full-text cache on disk
"""

from __future__ import annotations

from llmstxt_mcp.index import _connection
from llmstxt_mcp.index._cache import (
    cache_full_text,
    cache_path,
    cached_full_text,
    total_cache_size,
)
from llmstxt_mcp.index._connection import _close_conn_sync as _close_conn_sync, close
from llmstxt_mcp.index._entries import (
    add,
    clear_all,
    find,
    get,
    list_all,
    remove,
    search,
    summaries,
    summary,
)
from llmstxt_mcp.index._meta import read_meta, write_meta

__all__ = [
    "add",
    "cache_full_text",
    "cache_path",
    "cached_full_text",
    "clear_all",
    "close",
    "find",
    "get",
    "list_all",
    "read_meta",
    "remove",
    "search",
    "summaries",
    "summary",
    "total_cache_size",
    "write_meta",
]


def __getattr__(name: str) -> object:
    """Forward the connection singletons so callers can observe live state.

    The ``_conn`` / ``_init_lock`` globals live in ``_connection``; tests and the
    CLI read them via ``index._conn`` without importing the submodule.
    """
    if name in {"_conn", "_init_lock"}:
        return getattr(_connection, name)
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
