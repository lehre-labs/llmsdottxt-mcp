"""Read-only ``llmstxt://`` resource handler tests."""

from __future__ import annotations

import pytest

from llmsdottxt_mcp import index
from llmsdottxt_mcp.errors import PackageNotIndexedError
from llmsdottxt_mcp.models import Ecosystem, IndexEntry, ParsedLlmsTxt
from llmsdottxt_mcp.resources.packages import list_indexed_packages, package_entry


def _entry(package: str = "requests") -> IndexEntry:
    return IndexEntry(
        package=package,
        ecosystem=Ecosystem.python,
        latest_version="2.32.3",
        docs_base_url="https://requests.readthedocs.io",
        llms_txt=ParsedLlmsTxt(title="Requests"),
        indexed_at="2026-06-27T00:00:00Z",
    )


async def test_list_indexed_packages_returns_summaries() -> None:
    await index.add(_entry("requests"))
    await index.add(_entry("flask"))
    summaries = await list_indexed_packages()
    assert {s.package for s in summaries} == {"requests", "flask"}


async def test_list_indexed_packages_empty() -> None:
    assert await list_indexed_packages() == []


async def test_package_entry_returns_full_record() -> None:
    await index.add(_entry("requests"))
    entry = await package_entry("python", "requests")
    assert entry.package == "requests"
    assert entry.llms_txt.title == "Requests"


async def test_package_entry_missing_raises() -> None:
    with pytest.raises(PackageNotIndexedError):
        await package_entry("python", "never-indexed")
