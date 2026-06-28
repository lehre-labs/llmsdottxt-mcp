"""Server composition and tool-layer tests for the consolidated (v0.2) tool surface."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003 — used by fixture annotations
from unittest import mock

from fastmcp.exceptions import ToolError
import pytest

from llmsdottxt_mcp import index
from llmsdottxt_mcp.models import (
    BrowseToc,
    Ecosystem,
    IndexEntry,
    Link,
    ParsedLlmsTxt,
    Section,
    Transport,
)
from llmsdottxt_mcp.server import create_server
from llmsdottxt_mcp.tools import docs


def _entry(package: str, title: str | None = None) -> IndexEntry:
    title = title or package.title()
    return IndexEntry(
        package=package,
        ecosystem=Ecosystem.python,
        latest_version="1.0",
        docs_base_url="https://example.com",
        llms_txt=ParsedLlmsTxt(
            title=title,
            sections=[
                Section(
                    name="Core",
                    links=[
                        Link(title="Quickstart", url="https://example.com/qs"),
                        Link(title="API", url="https://example.com/api"),
                    ],
                ),
                Section(
                    name="Optional Guides",
                    optional=True,
                    links=[Link(title="Cookbook", url="https://example.com/cb")],
                ),
            ],
        ),
        indexed_at="2026-06-27T00:00:00Z",
    )


def test_create_server_registers_everything() -> None:
    server = create_server()
    assert server.name == "llmsdottxt-mcp"


# ── status ───────────────────────────────────────────────────────────


async def test_status_tool_empty() -> None:
    report = await docs.status()
    assert report.package_count == 0


# ── search (consolidated: empty query = all packages) ────────────────


async def test_search_empty_query_returns_all_packages() -> None:
    await index.add(_entry("requests"))
    await index.add(_entry("flask"))
    summaries = await docs.search("")
    assert {s.package for s in summaries} == {"requests", "flask"}


async def test_search_with_query_returns_ranked_hits() -> None:
    await index.add(_entry("requests"))
    await index.add(_entry("flask"))
    hits = await docs.search("requests")
    assert hits
    assert hits[0].package == "requests"


async def test_search_ecosystem_filter() -> None:
    await index.add(_entry("requests"))
    summaries = await docs.search("", "python")
    assert summaries
    assert all(s.ecosystem == Ecosystem.python for s in summaries)


# ── browse (consolidated: no section = TOC, section = full-text) ─────


async def test_browse_toc_returns_sections() -> None:
    await index.add(_entry("requests"))
    result = await docs.browse("requests")
    assert isinstance(result, BrowseToc)
    assert result.package == "requests"
    assert result.title == "Requests"
    assert len(result.sections) == 2
    assert result.sections[0].name == "Core"
    assert len(result.sections[0].links) == 2


async def test_browse_section_returns_full_text() -> None:
    index.cache_full_text("requests", "python", "# Full docs\n\nContent here.")
    await index.add(_entry("requests"))
    result = await docs.browse("requests", "core")
    assert isinstance(result, str)
    assert "Full docs" in result


async def test_browse_section_not_indexed_raises_tool_error() -> None:
    with pytest.raises(ToolError) as exc_info:
        await docs.browse("never-indexed")
    # Failure hint must steer the agent to the recovery tools.
    msg = str(exc_info.value)
    assert "index_deps" in msg
    assert "search" in msg


async def test_browse_section_no_full_text_non_fatal() -> None:
    await index.add(_entry("requests"))
    result = await docs.browse("requests", "core")
    assert isinstance(result, str)
    msg = result.lower()
    assert "no full documentation" in msg or "not available" in msg
    # Non-fatal result hints the next action (read the TOC).
    assert "browse" in msg


async def test_browse_ecosystem_disambiguation() -> None:
    await index.add(_entry("requests"))
    await index.add(
        IndexEntry(
            package="requests",
            ecosystem=Ecosystem.node,
            latest_version="1.0",
            docs_base_url="https://node.example.com",
            llms_txt=ParsedLlmsTxt(title="Node Requests"),
            indexed_at="2026-06-27T00:00:00Z",
        )
    )
    result = await docs.browse("requests", ecosystem="python")
    assert isinstance(result, BrowseToc)
    assert result.ecosystem == Ecosystem.python


# ── index_deps (replacement for scan_deps) ───────────────────────────


async def test_index_deps_returns_scan_report(tmp_path: Path) -> None:
    report = await docs.index_deps(root=str(tmp_path))
    assert report.scanned == 0


# ── serve transport ──────────────────────────────────────────────────


def test_serve_defaults_to_stdio() -> None:
    from llmsdottxt_mcp.server import serve as server_serve

    with mock.patch("llmsdottxt_mcp.server.mcp.run") as run_mock:
        server_serve()
        run_mock.assert_called_once_with(transport="stdio")


def test_serve_sse_transport() -> None:
    from llmsdottxt_mcp.server import serve as server_serve

    with mock.patch("llmsdottxt_mcp.server.mcp.run") as run_mock:
        server_serve(transport=Transport.sse)
        run_mock.assert_called_once_with(transport="sse", host="127.0.0.1", port=8000)


def test_serve_http_transport() -> None:
    from llmsdottxt_mcp.server import serve as server_serve

    with mock.patch("llmsdottxt_mcp.server.mcp.run") as run_mock:
        server_serve(transport=Transport.http)
        run_mock.assert_called_once_with(transport="streamable-http", host="127.0.0.1", port=8000)


def test_serve_custom_host_port() -> None:
    from llmsdottxt_mcp.server import serve as server_serve

    with mock.patch("llmsdottxt_mcp.server.mcp.run") as run_mock:
        server_serve(transport=Transport.http, host="0.0.0.0", port=3000)
        run_mock.assert_called_once_with(transport="streamable-http", host="0.0.0.0", port=3000)


def test_transport_to_fastmcp_mapping() -> None:
    assert Transport.stdio.to_fastmcp() == "stdio"
    assert Transport.sse.to_fastmcp() == "sse"
    assert Transport.http.to_fastmcp() == "streamable-http"
