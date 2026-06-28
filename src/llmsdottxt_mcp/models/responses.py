"""Tool-facing response models returned to MCP clients."""

from __future__ import annotations

from pydantic import Field

from llmsdottxt_mcp.models.core import Section, TrimmedModel
from llmsdottxt_mcp.models.strings import Ecosystem, Platform


class ScanReport(TrimmedModel):
    """Summary of a dependency scan."""

    project_root: str
    scanned: int = Field(description="Total dependencies discovered.")
    indexed: int = Field(description="Dependencies with a usable llms.txt.")
    missing: int = Field(description="Dependencies without discoverable docs.")
    blocked: int = Field(
        default=0,
        description="Dependencies whose docs host served a bot challenge (e.g. Cloudflare).",
    )
    ecosystems: list[Ecosystem] = Field(default_factory=list)


class PackageSummary(TrimmedModel):
    """One indexed package, as shown by search."""

    package: str
    ecosystem: Ecosystem
    version: str | None = None
    platform: Platform | None = None
    has_full_text: bool = False
    full_text_size: int = 0
    docs_base_url: str | None = None
    title: str | None = None


class SearchHit(TrimmedModel):
    """A ranked search result over the local index."""

    package: str
    ecosystem: Ecosystem
    score: int
    docs_base_url: str | None = None
    title: str | None = None
    has_full_text: bool = False
    full_text_size: int = 0


class BrowseToc(TrimmedModel):
    """Table-of-contents view of an indexed package (``browse(package)``)."""

    package: str
    ecosystem: Ecosystem
    title: str = ""
    description: str | None = None
    docs_base_url: str | None = None
    has_full_text: bool = False
    sections: list[Section] = Field(default_factory=list)


class StatusReport(TrimmedModel):
    """Index statistics."""

    ecosystems: list[str] = Field(default_factory=list)
    package_count: int = 0
    cache_size_bytes: int = 0
    last_scan: str | None = None
