"""Low-level SQL helpers shared across the index package.

Every function here takes an already-open connection and binds user values via
``?`` placeholders. Only the fixed ``_ENTRY_COLS`` column list is interpolated.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from llmsdottxt_mcp.models import (
    DocsUrlSource,
    Ecosystem,
    IndexEntry,
    ParsedLlmsTxt,
    Platform,
)

if TYPE_CHECKING:
    import aiosqlite

    from llmsdottxt_mcp.models import IndexMeta

_FTS_INSERT_SQL = (
    "INSERT INTO index_entry_fts(rowid, package, ecosystem, search_text) VALUES (?, ?, ?, ?)"
)
_FTS_DELETE_SQL = "DELETE FROM index_entry_fts WHERE rowid = ?"
# A fixed column list interpolated into SELECTs. It is a module constant, never
# user input, so the `# nosec B608` markers on those queries are accurate: every
# user-supplied value is bound via a `?` placeholder.
_ENTRY_COLS = (
    "package, ecosystem, version_spec, latest_version, docs_base_url, docs_url_source, "
    "repository_url, platform, has_full_text, full_text_size, indexed_at, llms_txt_json"
)


def _build_search_text(entry: IndexEntry) -> str:
    parts = [entry.package, entry.llms_txt.title]
    for section in entry.llms_txt.sections:
        parts.append(section.name)
        for link in section.links:
            parts.append(link.title)
            if link.description:
                parts.append(link.description)
    return " ".join(p for p in parts if p)


async def _insert_entry(conn: aiosqlite.Connection, entry: IndexEntry) -> None:
    llms_json = entry.llms_txt.model_dump_json()
    search_text = _build_search_text(entry)

    await conn.execute(
        f"INSERT OR REPLACE INTO index_entry ({_ENTRY_COLS}) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            entry.package,
            entry.ecosystem.value,
            entry.version_spec,
            entry.latest_version,
            entry.docs_base_url,
            entry.docs_url_source.value,
            entry.repository_url,
            entry.platform.value if entry.platform else None,
            int(entry.has_full_text),
            entry.full_text_size,
            entry.indexed_at,
            llms_json,
        ),
    )
    row = await conn.execute(
        "SELECT rowid FROM index_entry WHERE ecosystem = ? AND package = ?",
        (entry.ecosystem.value, entry.package),
    )
    found = await row.fetchone()
    if found is None:
        return
    rowid = found[0]
    await conn.execute(_FTS_DELETE_SQL, (rowid,))
    await conn.execute(_FTS_INSERT_SQL, (rowid, entry.package, entry.ecosystem.value, search_text))


def _row_to_entry(row: aiosqlite.Row) -> IndexEntry:
    return IndexEntry(
        package=row["package"],
        ecosystem=Ecosystem(row["ecosystem"]),
        version_spec=row["version_spec"],
        latest_version=row["latest_version"],
        docs_base_url=row["docs_base_url"],
        docs_url_source=DocsUrlSource(row["docs_url_source"]),
        repository_url=row["repository_url"],
        platform=Platform(row["platform"]) if row["platform"] else None,
        has_full_text=bool(row["has_full_text"]),
        full_text_size=row["full_text_size"],
        llms_txt=ParsedLlmsTxt.model_validate_json(row["llms_txt_json"]),
        indexed_at=row["indexed_at"],
    )


async def _upsert_meta(conn: aiosqlite.Connection, meta: IndexMeta) -> None:
    pairs = [
        ("version", str(meta.version)),
        ("last_scan", meta.last_scan or ""),
        ("project_root", meta.project_root or ""),
        ("ecosystems", json.dumps(meta.ecosystems)),
        ("package_count", str(meta.package_count)),
        ("packages", json.dumps(meta.packages)),
    ]
    for key, value in pairs:
        if value:
            await conn.execute(
                "INSERT OR REPLACE INTO index_meta (key, value) VALUES (?, ?)",
                (key, value),
            )
