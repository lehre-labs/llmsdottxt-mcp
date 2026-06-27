"""SQLite connection lifecycle, schema migrations, and one-time JSON import.

A single async connection is shared per process (WAL mode handles concurrent
reads + a single writer). The connection is created lazily on first use.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import json
import shutil

import aiosqlite

from llmsdottxt_mcp.config import settings
from llmsdottxt_mcp.index._sql import _insert_entry, _upsert_meta
from llmsdottxt_mcp.models import IndexEntry, IndexMeta

_conn: aiosqlite.Connection | None = None
_init_lock: asyncio.Lock | None = None

_MIGRATIONS: dict[int, str] = {
    1: """
        CREATE TABLE IF NOT EXISTS index_entry (
            package TEXT NOT NULL,
            ecosystem TEXT NOT NULL,
            version_spec TEXT,
            latest_version TEXT,
            docs_base_url TEXT,
            docs_url_source TEXT NOT NULL DEFAULT '',
            repository_url TEXT,
            platform TEXT,
            has_full_text INTEGER NOT NULL DEFAULT 0,
            full_text_size INTEGER NOT NULL DEFAULT 0,
            indexed_at TEXT NOT NULL,
            llms_txt_json TEXT NOT NULL DEFAULT '{}',
            PRIMARY KEY (ecosystem, package)
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS index_entry_fts USING fts5(
            package,
            ecosystem,
            search_text
        );

        CREATE TABLE IF NOT EXISTS index_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        INSERT OR IGNORE INTO index_meta (key, value) VALUES
            ('version', '1');
    """,
}


async def _get_conn() -> aiosqlite.Connection:
    global _conn, _init_lock  # noqa: PLW0603
    if _conn is not None:
        return _conn
    if _init_lock is None:
        _init_lock = asyncio.Lock()

    async with _init_lock:
        if _conn is not None:
            return _conn

        settings.ensure_dirs()
        _conn = await aiosqlite.connect(str(settings.index_db))
        await _conn.execute("PRAGMA journal_mode=WAL")
        await _conn.execute("PRAGMA foreign_keys=ON")
        _conn.row_factory = aiosqlite.Row
        await _run_migrations(_conn)
        await _maybe_import_json(_conn)
        return _conn


async def _close_conn() -> None:
    global _conn  # noqa: PLW0603
    if _conn is not None:
        await _conn.close()
        _conn = None


async def close() -> None:
    """Close the global database connection (for testing and CLI cleanup)."""
    await _close_conn()


def _close_conn_sync() -> None:
    """Synchronously null out the global connection reference.

    Used by test fixtures that cannot run async close. The old connection
    will be gc'd; SQLite tolerates this gracefully in WAL mode.
    """
    global _conn, _init_lock  # noqa: PLW0603
    _conn = None
    _init_lock = None


async def _run_migrations(conn: aiosqlite.Connection) -> None:
    await conn.execute(
        "CREATE TABLE IF NOT EXISTS _migrations "
        "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
    )
    applied = {row[0] async for row in await conn.execute("SELECT version FROM _migrations")}
    now = datetime.now(UTC).isoformat()
    for version, sql in sorted(_MIGRATIONS.items()):
        if version not in applied:
            await conn.executescript(sql)
            await conn.execute(
                "INSERT INTO _migrations (version, applied_at) VALUES (?, ?)", (version, now)
            )
    await conn.commit()


async def _maybe_import_json(conn: aiosqlite.Connection) -> None:
    old_index_dir = settings.index_root / "index"
    if not old_index_dir.is_dir():
        return

    cursor = await conn.execute("SELECT COUNT(*) FROM index_entry")
    row = await cursor.fetchone()
    if row is not None and row[0] > 0:
        return

    for eco_dir in sorted(old_index_dir.iterdir()):
        if not eco_dir.is_dir():
            continue
        for file in sorted(eco_dir.glob("*.json")):
            try:
                data = json.loads(file.read_text())
                entry = IndexEntry.model_validate(data)
                await _insert_entry(conn, entry)
            except json.JSONDecodeError, ValueError:
                pass

    old_meta = settings.index_root / "meta.json"
    if old_meta.is_file():
        try:
            meta = IndexMeta.model_validate_json(old_meta.read_text())
            await _upsert_meta(conn, meta)
            old_meta.unlink()
        except OSError, ValueError:
            pass

    await conn.commit()
    shutil.rmtree(old_index_dir, ignore_errors=True)
