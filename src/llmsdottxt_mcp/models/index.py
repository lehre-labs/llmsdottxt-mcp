"""Persisted index models — the on-disk shape of the local index."""

from __future__ import annotations

from pydantic import BaseModel, Field

from llmsdottxt_mcp.models.core import ParsedLlmsTxt
from llmsdottxt_mcp.models.strings import DocsUrlSource, Ecosystem, Platform


class IndexEntry(BaseModel):
    """One package's persisted index record (a row in the `index_entry` table)."""

    package: str
    ecosystem: Ecosystem
    version_spec: str | None = None
    latest_version: str | None = None
    docs_base_url: str | None = None
    docs_url_source: DocsUrlSource = DocsUrlSource.none
    repository_url: str | None = None
    platform: Platform | None = None
    has_full_text: bool = False
    full_text_size: int = 0
    llms_txt: ParsedLlmsTxt = Field(default_factory=ParsedLlmsTxt)
    indexed_at: str


class IndexMeta(BaseModel):
    """Global scan metadata (key/value rows in the `index_meta` table)."""

    version: int = 1
    last_scan: str | None = None
    project_root: str | None = None
    ecosystems: list[str] = Field(default_factory=list)
    package_count: int = 0
    packages: dict[str, list[str]] = Field(default_factory=dict)
