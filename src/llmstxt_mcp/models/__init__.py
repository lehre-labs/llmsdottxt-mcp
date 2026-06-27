"""Typed domain and response models for llmstxt-mcp."""

from __future__ import annotations

from llmstxt_mcp.models.core import (
    Dependency,
    DocsInfo,
    Link,
    LlmsTxtResult,
    ParsedLlmsTxt,
    PlatformHint,
    Section,
)
from llmstxt_mcp.models.index import IndexEntry, IndexMeta
from llmstxt_mcp.models.responses import (
    BrowseToc,
    PackageSummary,
    ScanReport,
    SearchHit,
    StatusReport,
)
from llmstxt_mcp.models.strings import (
    DocsUrlSource,
    Ecosystem,
    HttpUrlString,
    LogLevel,
    NonEmptyText,
    PackageName,
    Platform,
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
    "ScanReport",
    "SearchHit",
    "SearchQuery",
    "Section",
    "StatusReport",
    "Transport",
]
