"""Typed domain and response models for llmsdottxt-mcp."""

from __future__ import annotations

from llmsdottxt_mcp.models.core import (
    Dependency,
    DocsInfo,
    Link,
    LlmsTxtResult,
    ParsedLlmsTxt,
    PlatformHint,
    Section,
)
from llmsdottxt_mcp.models.index import IndexEntry, IndexMeta
from llmsdottxt_mcp.models.responses import (
    BrowseToc,
    PackageSummary,
    ScanReport,
    SearchHit,
    StatusReport,
)
from llmsdottxt_mcp.models.strings import (
    DocsUrlSource,
    Ecosystem,
    HttpUrlString,
    LogLevel,
    NonEmptyText,
    PackageName,
    Platform,
    ResultLimit,
    ResultOffset,
    SearchQuery,
    Transport,
)

__all__ = [
    "BrowseToc",
    "Dependency",
    "DocsInfo",
    "DocsUrlSource",
    "Ecosystem",
    "HttpUrlString",
    "IndexEntry",
    "IndexMeta",
    "Link",
    "LlmsTxtResult",
    "LogLevel",
    "NonEmptyText",
    "PackageName",
    "PackageSummary",
    "ParsedLlmsTxt",
    "Platform",
    "PlatformHint",
    "ResultLimit",
    "ResultOffset",
    "ScanReport",
    "SearchHit",
    "SearchQuery",
    "Section",
    "StatusReport",
    "Transport",
]
