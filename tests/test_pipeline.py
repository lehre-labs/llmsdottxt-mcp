"""End-to-end pipeline tests (network mocked)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from llmstxt_mcp import index, pipeline
from llmstxt_mcp.errors import PackageNotIndexedError

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_httpx import HTTPXMock


@pytest.fixture
def single_dep_project(tmp_path: Path) -> Path:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        '[project]\nname="x"\nversion="0"\ndependencies=["requests"]\n'
    )
    return project


def _mock_requests(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://pypi.org/pypi/requests/json",
        json={
            "info": {
                "version": "2.32.3",
                "home_page": "https://requests.readthedocs.io",
                "project_urls": {"Documentation": "https://requests.readthedocs.io"},
            }
        },
    )
    httpx_mock.add_response(url="https://requests.readthedocs.io", text="")
    httpx_mock.add_response(
        url="https://requests.readthedocs.io/llms.txt",
        text="# Requests\n\n> HTTP for humans.\n\n## Guide\n\n- [Quickstart](https://x): start\n",
    )
    httpx_mock.add_response(
        url="https://requests.readthedocs.io/llms-full.txt", text="FULL DOCS BODY"
    )


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_scan_indexes_package(single_dep_project: Path, httpx_mock: HTTPXMock) -> None:
    _mock_requests(httpx_mock)
    report = await pipeline.scan_project(single_dep_project)

    assert report.scanned == 1
    assert report.indexed == 1
    entry = await index.get("requests", "python")
    assert entry is not None
    assert entry.llms_txt.title == "Requests"
    assert entry.has_full_text is True


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_get_full_text_uses_cache(single_dep_project: Path, httpx_mock: HTTPXMock) -> None:
    _mock_requests(httpx_mock)
    await pipeline.scan_project(single_dep_project)

    content = await pipeline.get_full_text("requests")
    assert content == "FULL DOCS BODY"


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_scan_counts_cloudflare_blocked(tmp_path: Path, httpx_mock: HTTPXMock) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        '[project]\nname="x"\nversion="0"\ndependencies=["walled"]\n'
    )
    httpx_mock.add_response(
        url="https://pypi.org/pypi/walled/json",
        json={
            "info": {
                "version": "1.0.0",
                "project_urls": {"Documentation": "https://docs.walled.com"},
            }
        },
    )
    # Docs host is behind a Cloudflare bot wall.
    httpx_mock.add_response(
        url="https://docs.walled.com",
        status_code=403,
        headers={"cf-mitigated": "challenge"},
    )

    report = await pipeline.scan_project(project)

    assert report.scanned == 1
    assert report.indexed == 0
    assert report.blocked == 1
    assert await index.get("walled", "python") is None


async def test_scan_no_manifest(tmp_path: Path) -> None:
    report = await pipeline.scan_project(tmp_path)
    assert report.scanned == 0


async def test_get_full_text_not_indexed() -> None:
    with pytest.raises(PackageNotIndexedError):
        await pipeline.get_full_text("never-indexed")


async def test_scan_empty_deps(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        '[project]\nname="x"\nversion="0"\ndependencies=["python"]\n'
    )
    report = await pipeline.scan_project(project)
    assert report.scanned == 0


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_scan_resolve_returns_none(tmp_path: Path, httpx_mock: HTTPXMock) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        '[project]\nname="x"\nversion="0"\ndependencies=["unknown"]\n'
    )
    httpx_mock.add_response(url="https://pypi.org/pypi/unknown/json", status_code=404)
    report = await pipeline.scan_project(project)
    assert report.scanned == 1
    assert report.missing == 1
    assert report.indexed == 0


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_scan_fetch_llms_txt_none(tmp_path: Path, httpx_mock: HTTPXMock) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        '[project]\nname="x"\nversion="0"\ndependencies=["nodocs"]\n'
    )
    httpx_mock.add_response(
        url="https://pypi.org/pypi/nodocs/json",
        json={
            "info": {
                "version": "1.0",
                "project_urls": {"Documentation": "https://docs.nodocs.com"},
            }
        },
    )
    httpx_mock.add_response(url="https://docs.nodocs.com", text="")
    httpx_mock.add_response(url="https://docs.nodocs.com/llms.txt", status_code=404)
    httpx_mock.add_response(url="https://docs.nodocs.com/llms-full.txt", status_code=404)
    report = await pipeline.scan_project(project)
    assert report.scanned == 1
    assert report.missing == 1
    assert report.indexed == 0


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_get_full_text_fetches_on_demand(
    single_dep_project: Path, httpx_mock: HTTPXMock
) -> None:
    _mock_requests(httpx_mock)
    await pipeline.scan_project(single_dep_project)

    # Clear the cache to force a fetch on demand.
    await index.clear_all()
    # Re-index with just the entry, no cache.
    from llmstxt_mcp.models import (
        Ecosystem,
        IndexEntry,
        Link,
        ParsedLlmsTxt,
        Platform,
        Section,
    )

    httpx_mock.add_response(
        url="https://requests.readthedocs.io/llms-full.txt", text="FRESH FULL DOCS"
    )
    await index.add(
        IndexEntry(
            package="requests",
            ecosystem=Ecosystem.python,
            docs_base_url="https://requests.readthedocs.io",
            platform=Platform.readthedocs,
            has_full_text=False,
            full_text_size=0,
            llms_txt=ParsedLlmsTxt(
                title="Requests",
                sections=[Section(name="Guide", links=[Link(title="x", url="u")])],
            ),
            indexed_at="2026-06-27T00:00:00Z",
        )
    )
    # Platform detection probe.
    httpx_mock.add_response(url="https://requests.readthedocs.io", text="")

    content = await pipeline.get_full_text("requests")
    assert content == "FRESH FULL DOCS"
