"""Index entry CRUD, ranked FTS5 search, summaries, and bulk clear."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

from llmsdottxt_mcp.config import settings
from llmsdottxt_mcp.index._connection import _get_conn
from llmsdottxt_mcp.index._sql import (
    _ENTRY_COLS,
    _FTS_DELETE_SQL,
    _insert_entry,
    _row_to_entry,
)
from llmsdottxt_mcp.models import PackageSummary, SearchHit

if TYPE_CHECKING:
    from llmsdottxt_mcp.models import IndexEntry


async def add(entry: IndexEntry) -> None:
    conn = await _get_conn()
    await _insert_entry(conn, entry)
    await conn.commit()


async def get(package: str, ecosystem: str) -> IndexEntry | None:
    conn = await _get_conn()
    cursor = await conn.execute(
        f"SELECT {_ENTRY_COLS} FROM index_entry WHERE package = ? AND ecosystem = ?",  # nosec B608
        (package, ecosystem),
    )
    row = await cursor.fetchone()
    return _row_to_entry(row) if row else None


async def find(package: str, ecosystem: str | None = None) -> IndexEntry | None:
    conn = await _get_conn()
    if ecosystem:
        return await get(package, ecosystem)
    cursor = await conn.execute(
        f"SELECT {_ENTRY_COLS} FROM index_entry WHERE package = ? LIMIT 1",  # nosec B608
        (package,),
    )
    row = await cursor.fetchone()
    return _row_to_entry(row) if row else None


async def list_all(ecosystem: str | None = None) -> list[IndexEntry]:
    conn = await _get_conn()
    if ecosystem:
        cursor = await conn.execute(
            f"SELECT {_ENTRY_COLS} FROM index_entry WHERE ecosystem = ? ORDER BY package",  # nosec B608
            (ecosystem,),
        )
    else:
        cursor = await conn.execute(
            f"SELECT {_ENTRY_COLS} FROM index_entry ORDER BY ecosystem, package"  # nosec B608
        )
    return [_row_to_entry(row) async for row in cursor]


async def remove(package: str, ecosystem: str) -> bool:
    conn = await _get_conn()
    row = await conn.execute(
        "SELECT rowid FROM index_entry WHERE package = ? AND ecosystem = ?",
        (package, ecosystem),
    )
    found = await row.fetchone()
    if found is None:
        return False
    rowid = found[0]
    await conn.execute(_FTS_DELETE_SQL, (rowid,))
    await conn.execute(
        "DELETE FROM index_entry WHERE package = ? AND ecosystem = ?",
        (package, ecosystem),
    )
    await conn.commit()
    return True


def summary(entry: IndexEntry) -> PackageSummary:
    return PackageSummary(
        package=entry.package,
        ecosystem=entry.ecosystem,
        version=entry.latest_version or entry.version_spec,
        platform=entry.platform,
        has_full_text=entry.has_full_text,
        full_text_size=entry.full_text_size,
        docs_base_url=entry.docs_base_url,
        title=entry.llms_txt.title or None,
    )


async def summaries(ecosystem: str | None = None) -> list[PackageSummary]:
    return [summary(entry) for entry in await list_all(ecosystem)]


async def search(query: str, limit: int = 10) -> list[SearchHit]:
    conn = await _get_conn()
    terms = [t for t in query.split() if t]
    if not terms:
        return []

    # Wrap each term as an FTS5 string literal, doubling any embedded quote so
    # user input cannot break out of the literal (FTS5's escape rule).
    fts_query = " OR ".join(f'"{term.replace('"', '""')}"' for term in terms)
    cursor = await conn.execute(
        "SELECT rowid, rank FROM index_entry_fts "
        "WHERE index_entry_fts MATCH ? ORDER BY rank LIMIT ?",
        (fts_query, limit),
    )
    fts_rows = [(row[0], row[1]) async for row in cursor]
    if not fts_rows:
        return []

    rowids = [r[0] for r in fts_rows]

    placeholders = ",".join("?" * len(rowids))
    cursor = await conn.execute(
        f"SELECT rowid, {_ENTRY_COLS} FROM index_entry WHERE rowid IN ({placeholders})",  # nosec B608
        rowids,
    )
    entry_by_rowid: dict[int, IndexEntry] = {}
    async for row in cursor:
        entry_by_rowid[row[0]] = _row_to_entry(row)

    hits: list[SearchHit] = []
    for rowid, rank in fts_rows:
        entry = entry_by_rowid.get(rowid)
        if entry is None:
            continue
        hits.append(
            SearchHit(
                package=entry.package,
                ecosystem=entry.ecosystem,
                score=int(-rank),
                docs_base_url=entry.docs_base_url,
                title=entry.llms_txt.title or None,
                has_full_text=entry.has_full_text,
                full_text_size=entry.full_text_size,
            )
        )
    return hits


async def clear_all() -> None:
    conn = await _get_conn()
    await conn.execute("DELETE FROM index_entry_fts")
    await conn.execute("DELETE FROM index_entry")
    await conn.execute("DELETE FROM index_meta")
    await conn.commit()
    if settings.cache_dir.is_dir():
        shutil.rmtree(settings.cache_dir)
        settings.cache_dir.mkdir(parents=True, exist_ok=True)
