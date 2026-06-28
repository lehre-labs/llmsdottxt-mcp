"""Constrained string aliases and finite enums for validation boundaries."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, StringConstraints

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


class Ecosystem(StrEnum):
    """Supported package ecosystems."""

    python = "python"
    node = "node"
    rust = "rust"
    go = "go"


class Platform(StrEnum):
    """Known documentation hosting platforms."""

    mintlify = "mintlify"
    readthedocs = "readthedocs"
    readme = "readme"
    docusaurus = "docusaurus"
    gitbook = "gitbook"
    redocly = "redocly"
    mkdocs = "mkdocs"
    github_pages = "github_pages"
    vitepress = "vitepress"
    starlight = "starlight"
    sphinx = "sphinx"


class DocsUrlSource(StrEnum):
    """Where a resolved documentation URL came from."""

    pypi_project_urls = "pypi_project_urls"
    registry_documentation = "registry_documentation"
    homepage_fallback = "homepage_fallback"
    github_pages = "github_pages"
    none = "none"


PackageName = Annotated[
    str,
    StringConstraints(
        min_length=1, max_length=214, strip_whitespace=True, pattern=r"^[A-Za-z0-9._-]+$"
    ),
    Field(description="Distribution / package name."),
]

NonEmptyText = Annotated[
    str,
    StringConstraints(min_length=1, strip_whitespace=True),
    Field(description="Non-empty text."),
]

HttpUrlString = Annotated[
    str,
    StringConstraints(pattern=r"^https?://"),
    Field(description="HTTP(S) URL serialized as a string."),
]

SearchQuery = Annotated[
    str,
    StringConstraints(min_length=1, strip_whitespace=True),
    Field(description="Documentation search term."),
]

ResultLimit = Annotated[
    int,
    Field(ge=1, le=100, description="Maximum number of results to return."),
]

ResultOffset = Annotated[
    int,
    Field(ge=0, description="Number of results to skip, for pagination."),
]


class Transport(StrEnum):
    """MCP server transport protocols (user-facing names)."""

    stdio = "stdio"
    sse = "sse"
    http = "http"

    def to_fastmcp(self) -> Literal["stdio", "sse", "streamable-http"]:
        """Map to FastMCP's internal transport name."""
        if self is Transport.http:
            return "streamable-http"
        if self is Transport.sse:
            return "sse"
        return "stdio"
