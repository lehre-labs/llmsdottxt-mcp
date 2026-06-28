"""Index storage, search, and cache tests."""

from __future__ import annotations

from llmsdottxt_mcp import index
from llmsdottxt_mcp.models import (
    Ecosystem,
    IndexEntry,
    IndexMeta,
    Link,
    ParsedLlmsTxt,
    Platform,
    Section,
)


def _entry(package: str = "requests", title: str = "Requests") -> IndexEntry:
    return IndexEntry(
        package=package,
        ecosystem=Ecosystem.python,
        latest_version="2.32.3",
        docs_base_url="https://requests.readthedocs.io",
        platform=Platform.readthedocs,
        has_full_text=True,
        full_text_size=1234,
        llms_txt=ParsedLlmsTxt(
            title=title,
            sections=[Section(name="Auth", links=[Link(title="Authentication", url="u")])],
        ),
        indexed_at="2026-06-27T00:00:00Z",
    )


async def test_add_get_roundtrip() -> None:
    await index.add(_entry())
    got = await index.get("requests", "python")
    assert got is not None
    assert got.platform == Platform.readthedocs
    assert got.ecosystem == Ecosystem.python


async def test_find_across_ecosystems() -> None:
    await index.add(_entry())
    assert await index.find("requests") is not None
    assert await index.find("absent") is None


async def test_list_and_summaries() -> None:
    await index.add(_entry("a"))
    await index.add(_entry("b"))
    assert {e.package for e in await index.list_all()} == {"a", "b"}
    summaries = await index.summaries()
    assert all(s.version == "2.32.3" for s in summaries)


async def test_remove() -> None:
    await index.add(_entry())
    assert await index.remove("requests", "python") is True
    assert await index.get("requests", "python") is None


async def test_search_ranks_package_name() -> None:
    await index.add(_entry("requests"))
    await index.add(_entry("flask", title="Flask"))
    hits = await index.search("requests")
    assert hits
    assert hits[0].package == "requests"


async def test_search_matches_link_titles() -> None:
    await index.add(_entry())
    hits = await index.search("authentication")
    assert hits
    assert hits[0].package == "requests"


def test_cache_roundtrip() -> None:
    index.cache_full_text("requests", "python", "hello world")
    assert index.cached_full_text("requests", "python") == "hello world"
    assert index.total_cache_size() > 0


async def test_meta_roundtrip() -> None:
    await index.write_meta(IndexMeta(package_count=3, ecosystems=["python"]))
    meta = await index.read_meta()
    assert meta.package_count == 3
    assert meta.ecosystems == ["python"]


async def test_clear_all() -> None:
    await index.add(_entry())
    index.cache_full_text("requests", "python", "data")
    await index.clear_all()
    assert await index.list_all() == []
    assert index.total_cache_size() == 0


async def test_remove_nonexistent() -> None:
    assert await index.remove("nope", "python") is False


async def test_get_nonexistent() -> None:
    assert await index.get("nope", "python") is None


def test_cached_full_text_missing() -> None:
    assert index.cached_full_text("never", "python") is None


def test_total_cache_size_no_dir() -> None:
    assert index.total_cache_size() == 0


async def test_summaries_filtered_by_ecosystem() -> None:
    await index.add(_entry("a"))
    await index.add(_entry("b"))
    summaries = await index.summaries("python")
    assert all(s.ecosystem == Ecosystem.python for s in summaries)


async def test_list_all_filtered_by_ecosystem() -> None:
    await index.add(_entry("a"))
    await index.add(_entry("b"))
    entries = await index.list_all("python")
    assert len(entries) == 2


async def test_list_all_empty_dir() -> None:
    assert await index.list_all("nonexistent") == []


async def test_read_meta_default_when_empty() -> None:
    meta = await index.read_meta()
    assert meta.last_scan is None


async def test_read_meta_persists() -> None:
    await index.write_meta(IndexMeta(ecosystems=["python"]))
    meta = await index.read_meta()
    assert meta.ecosystems == ["python"]
    assert meta.last_scan is None


async def test_list_all_pagination() -> None:
    for name in ("a", "b", "c", "d"):
        await index.add(_entry(name))
    assert [e.package for e in await index.list_all(limit=2)] == ["a", "b"]
    assert [e.package for e in await index.list_all(limit=2, offset=2)] == ["c", "d"]


async def test_summaries_pagination() -> None:
    for name in ("a", "b", "c"):
        await index.add(_entry(name))
    page = await index.summaries(limit=1, offset=1)
    assert [s.package for s in page] == ["b"]


async def test_search_pagination() -> None:
    for name in ("req1", "req2", "req3"):
        await index.add(_entry(name, title="requests"))
    first = await index.search("requests", limit=2)
    assert len(first) == 2
    second = await index.search("requests", limit=2, offset=2)
    assert len(second) == 1
    # No page overlap.
    assert {h.package for h in first}.isdisjoint({h.package for h in second})


async def test_search_filters_by_ecosystem() -> None:
    await index.add(_entry("requests"))
    await index.add(
        IndexEntry(
            package="axios",
            ecosystem=Ecosystem.node,
            llms_txt=ParsedLlmsTxt(title="axios requests"),
            indexed_at="2026-06-27T00:00:00Z",
        )
    )
    hits = await index.search("requests", ecosystem="node")
    assert [h.package for h in hits] == ["axios"]


async def test_search_no_results() -> None:
    await index.add(_entry("requests"))
    assert await index.search("zzznotfound") == []


async def test_search_with_double_quote_does_not_crash() -> None:
    """A query containing FTS5 special characters must not raise."""
    await index.add(_entry("requests"))
    assert await index.search('foo"bar') == []
    # A quoted package name term still matches once escaped.
    assert await index.search('requests"') != []


async def test_search_blank_query_returns_empty() -> None:
    await index.add(_entry("requests"))
    assert await index.search("   ") == []


def test_summary_null_title() -> None:
    entry = _entry("pkg")
    entry.llms_txt.title = ""
    s = index.summary(entry)
    assert s.title is None


async def test_imports_legacy_json_index(tmp_index) -> None:
    """First connect migrates a pre-existing file-per-package JSON index (ADR-0004)."""
    old_dir = tmp_index / "index" / "python"
    old_dir.mkdir(parents=True)
    (old_dir / "requests.json").write_text(_entry("requests").model_dump_json())
    # An unreadable file must be skipped, not abort the migration.
    (old_dir / "broken.json").write_text("{ not json")
    (tmp_index / "meta.json").write_text(
        IndexMeta(
            package_count=1, ecosystems=["python"], last_scan="2026-06-27T00:00:00Z"
        ).model_dump_json()
    )

    # Any index call triggers the lazy connect + auto-import.
    entries = await index.list_all()

    assert [e.package for e in entries] == ["requests"]
    assert not (tmp_index / "index").exists()  # old dir removed after import
    assert not (tmp_index / "meta.json").exists()
    meta = await index.read_meta()
    assert meta.ecosystems == ["python"]
