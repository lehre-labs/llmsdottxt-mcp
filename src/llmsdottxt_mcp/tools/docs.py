"""MCP tools: index_deps, search, browse, status."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from fastmcp.exceptions import ToolError

from llmsdottxt_mcp import index, pipeline
from llmsdottxt_mcp.errors import LlmstxtError, SectionNotFoundError
from llmsdottxt_mcp.models import (
    BrowseToc,
    PackageName,
    PackageSummary,
    ResultLimit,
    ResultOffset,
    ScanReport,
    SearchHit,
    SearchQuery,
    StatusReport,
)

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    mcp.tool(index_deps)
    mcp.tool(search)
    mcp.tool(browse)
    mcp.tool(status)


async def index_deps(root: str | None = None, refresh: bool = False) -> ScanReport:
    """Scan project dependencies, discover & fetch llms.txt, build the local index.

    ## Using this tool
    Call this first on a new project to populate the index. Afterwards, use
    **search** to list or find packages, then **browse** to read their docs.

    Args:
        root: Project root path. Defaults to the current working directory.
        refresh: Re-fetch docs even for already-indexed packages.
    """
    project_root = Path(root).resolve() if root else Path.cwd()
    return await pipeline.scan_project(project_root, refresh=refresh)


async def search(
    query: SearchQuery | None = None,
    ecosystem: str | None = None,
    limit: ResultLimit = 20,
    offset: ResultOffset = 0,
) -> list[PackageSummary] | list[SearchHit]:
    """Search indexed documentation or list all packages when query is empty.

    ## Using this tool
    Call with a query string for ranked full-text search. Call with no query
    (or an empty string) to list every indexed package with version, platform,
    and full-text availability. Results are paginated; raise ``offset`` by
    ``limit`` to page through more. Use **index_deps** first if the index is empty.

    Args:
        query: Free-text search term. Omit or pass empty for a full listing.
        ecosystem: Filter results by ecosystem (python, node, rust, go).
        limit: Maximum number of results to return (1-100, default 20).
        offset: Number of results to skip, for pagination (default 0).
    """
    if not query:
        return await index.summaries(ecosystem, limit, offset)
    return await index.search(query, ecosystem, limit, offset)


async def browse(
    package: PackageName, section: str | None = None, ecosystem: str | None = None
) -> BrowseToc | str:
    """Browse a package's TOC or read full-text documentation for a section.

    ## Using this tool
    Call without ``section`` to get the table of contents (title, description,
    and all sections with their links). Call with a section name to retrieve a
    single page of the full-text docs, matched by its title. Use **search**
    first if you need to discover which packages are available.

    Args:
        package: Package name (e.g. 'requests', 'fastapi').
        section: Optional page title from the docs. When absent, returns TOC.
                 Matched case-insensitively against llms-full.txt page headings.
        ecosystem: Disambiguate when the same package name exists in multiple
                   ecosystems (e.g. 'requests' in both python and node).
    """
    entry = await index.find(package, ecosystem)
    if entry is None:
        msg = (
            f"No indexed package named '{package}'. Run index_deps to scan this "
            f"project's dependencies, or call search with an empty query to list "
            f"everything already indexed."
        )
        raise ToolError(msg)

    if section is None:
        return BrowseToc(
            package=entry.package,
            ecosystem=entry.ecosystem,
            title=entry.llms_txt.title,
            description=entry.llms_txt.description,
            docs_base_url=entry.docs_base_url,
            has_full_text=entry.has_full_text,
            sections=entry.llms_txt.sections,
        )

    try:
        return await pipeline.get_section(package, section, entry.ecosystem.value)
    except SectionNotFoundError as exc:
        available = ", ".join(exc.available[:30]) or "(none — full text has no page headings)"
        return (
            f"No page titled '{section}' in '{package}'. Available pages: {available}. "
            f"Pass one of these as the section, or call browse('{package}') for the TOC."
        )
    except LlmstxtError as exc:
        # Non-fatal: the package is indexed but has no llms-full.txt. Steer the
        # agent back to the TOC rather than surfacing a dead end.
        return f"{exc} Call browse('{package}') without a section to read its table-of-contents links instead."


async def status() -> StatusReport:
    """Get index statistics: package count, ecosystems, cache size, last scan.

    ## Using this tool
    Call to check whether the index is populated before using **search** or
    **browse**. After **index_deps**, use this to verify the scan was successful.
    """
    meta = await index.read_meta()
    entries = await index.list_all()
    return StatusReport(
        ecosystems=meta.ecosystems,
        package_count=len(entries),
        cache_size_bytes=index.total_cache_size(),
        last_scan=meta.last_scan,
    )
