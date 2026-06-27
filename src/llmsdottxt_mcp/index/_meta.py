"""Index metadata persistence (the ``index_meta`` key/value table)."""

from __future__ import annotations

import json

from llmsdottxt_mcp.index._connection import _get_conn
from llmsdottxt_mcp.index._sql import _upsert_meta
from llmsdottxt_mcp.models import IndexMeta


async def read_meta() -> IndexMeta:
    conn = await _get_conn()
    cursor = await conn.execute("SELECT key, value FROM index_meta")
    raw = {row[0]: row[1] async for row in cursor}

    return IndexMeta(
        version=int(raw.get("version", "1")),
        last_scan=raw.get("last_scan"),
        project_root=raw.get("project_root"),
        ecosystems=json.loads(raw["ecosystems"]) if "ecosystems" in raw else [],
        package_count=int(raw.get("package_count", "0")),
        packages=json.loads(raw["packages"]) if "packages" in raw else {},
    )


async def write_meta(meta: IndexMeta) -> None:
    conn = await _get_conn()
    await _upsert_meta(conn, meta)
    await conn.commit()
