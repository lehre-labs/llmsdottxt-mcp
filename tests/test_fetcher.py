"""Fetcher and parser tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmsdottxt_mcp.fetcher import (
    _shares_repo_host,
    fetch_full_text,
    fetch_llms_txt,
    parse_llms_txt,
)
from llmsdottxt_mcp.http import build_client
from llmsdottxt_mcp.models import DocsInfo, Ecosystem

if TYPE_CHECKING:
    import pytest
    from pytest_httpx import HTTPXMock


def test_parse_llms_txt(sample_llms_txt: str) -> None:
    parsed = parse_llms_txt(sample_llms_txt)
    assert parsed.title == "Requests: HTTP for Humans"
    assert parsed.description is not None
    assert "elegant" in parsed.description
    assert [s.name for s in parsed.sections] == ["Core Documentation", "Optional"]
    assert parsed.sections[1].optional is True
    assert parsed.sections[0].links[0].title == "Quickstart"
    assert parsed.sections[0].links[0].description == "Get started"


def test_parse_empty() -> None:
    parsed = parse_llms_txt("")
    assert parsed.title == ""
    assert parsed.sections == []


async def test_fetch_llms_txt(httpx_mock: HTTPXMock, sample_llms_txt: str) -> None:
    httpx_mock.add_response(url="https://docs.example.com/llms.txt", text=sample_llms_txt)
    info = DocsInfo(
        package="demo", ecosystem=Ecosystem.python, docs_base_url="https://docs.example.com"
    )
    async with build_client() as client:
        result = await fetch_llms_txt(info, None, client)
    assert result is not None
    assert result.parsed.title == "Requests: HTTP for Humans"


async def test_fetch_rejects_html_homepage(httpx_mock: HTTPXMock) -> None:
    """A homepage-fallback URL with a #fragment must not yield a repo's HTML page.

    The fragment is stripped (so the request is .../repo/llms.txt, proving the
    fix), and an HTML 200 is rejected rather than counted as a real llms.txt.
    """
    httpx_mock.add_response(
        url="https://github.com/owner/repo/llms.txt",
        text="<!DOCTYPE html><html><body>a repo page</body></html>",
        headers={"content-type": "text/html; charset=utf-8"},
    )
    info = DocsInfo(
        package="repo",
        ecosystem=Ecosystem.node,
        docs_base_url="https://github.com/owner/repo#readme",
        repository_url="https://github.com/owner/repo",
    )
    async with build_client() as client:
        assert await fetch_llms_txt(info, None, client) is None


async def test_fetch_rejects_contentless_body(httpx_mock: HTTPXMock) -> None:
    """A 200 that parses to no title and no sections is not a real llms.txt."""
    httpx_mock.add_response(
        url="https://docs.example.com/llms.txt",
        text="just some prose with no heading and no link list",
        headers={"content-type": "text/plain"},
    )
    info = DocsInfo(
        package="demo", ecosystem=Ecosystem.python, docs_base_url="https://docs.example.com"
    )
    async with build_client() as client:
        assert await fetch_llms_txt(info, None, client) is None


async def test_fetch_falls_back_to_host_root(httpx_mock: HTTPXMock, sample_llms_txt: str) -> None:
    """A deep docs path 404s, but the host-root llms.txt is found (e.g. ai-sdk.dev)."""
    httpx_mock.add_response(url="https://ai-sdk.dev/docs/llms.txt", status_code=404)
    httpx_mock.add_response(
        url="https://ai-sdk.dev/llms.txt",
        text=sample_llms_txt,
        headers={"content-type": "text/plain"},
    )
    info = DocsInfo(package="ai", ecosystem=Ecosystem.node, docs_base_url="https://ai-sdk.dev/docs")
    async with build_client() as client:
        result = await fetch_llms_txt(info, None, client)
    assert result is not None
    assert result.url == "https://ai-sdk.dev/llms.txt"


def test_shares_repo_host_covers_any_forge() -> None:
    """Forge detection is by repo-host match, so self-hosted forges work too."""
    # docs URL == a repo page on the same host as the source -> treated as forge.
    assert _shares_repo_host("codeberg.org", "https://codeberg.org/owner/repo")
    assert _shares_repo_host("git.example.com", "https://git.example.com/o/r")  # self-hosted
    assert _shares_repo_host("GitHub.com", "https://github.com/o/r")  # case-insensitive
    # A real docs domain differs from the repo host -> not a forge, root is probed.
    assert not _shares_repo_host("ai-sdk.dev", "https://github.com/vercel/ai")
    assert not _shares_repo_host("docs.pola.rs", None)


async def test_fetch_full_text_truncates(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    from llmsdottxt_mcp.config import settings

    monkeypatch.setattr(settings, "max_full_text_size", 10)
    httpx_mock.add_response(url="https://docs.example.com/llms-full.txt", text="x" * 500)
    info = DocsInfo(
        package="demo", ecosystem=Ecosystem.python, docs_base_url="https://docs.example.com"
    )
    async with build_client() as client:
        content = await fetch_full_text(info, None, client)
    assert content is not None
    assert "truncated" in content.lower()


async def test_fetch_full_text_missing(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://docs.example.com/llms-full.txt", status_code=404)
    info = DocsInfo(
        package="demo", ecosystem=Ecosystem.python, docs_base_url="https://docs.example.com"
    )
    async with build_client() as client:
        assert await fetch_full_text(info, None, client) is None


def test_parse_ignores_headings_inside_fenced_code_blocks() -> None:
    raw = (
        "# Project\n\n"
        "## Real Section\n\n"
        "- [Link](url)\n\n"
        "```python\n"
        "# not a heading\n"
        "## also not a heading\n"
        "### nope\n"
        "print(1)\n"
        "```\n\n"
        "## After Code\n\n"
        "- [Safe](url2)\n"
    )
    parsed = parse_llms_txt(raw)
    assert parsed.title == "Project"
    assert [s.name for s in parsed.sections] == ["Real Section", "After Code"]


def test_parse_handles_h3_to_h6_headings() -> None:
    raw = (
        "# Title\n\n"
        "> A description.\n\n"
        "## Top\n\n"
        "- [A](a)\n\n"
        "### Nested\n\n"
        "- [B](b)\n\n"
        "###### Deep\n\n"
        "- [C](c)\n\n"
        "## Another Top\n\n"
        "- [D](d)\n"
    )
    parsed = parse_llms_txt(raw)
    assert parsed.title == "Title"
    assert parsed.description == "A description."
    levels = [(s.name, s.level) for s in parsed.sections]
    assert levels == [
        ("Top", 2),
        ("Nested", 3),
        ("Deep", 6),
        ("Another Top", 2),
    ]


def test_parse_handles_indented_headings() -> None:
    raw = "# Title\n\n  ## Indented H2  \n\n- [Link](url)\n\n   ### Indented H3\n\n- [Sub](url2)\n"
    parsed = parse_llms_txt(raw)
    names = [s.name for s in parsed.sections]
    assert names == ["Indented H2", "Indented H3"]


def test_parse_preserves_link_descriptions() -> None:
    raw = "# Title\n\n## Section\n\n- [Link](url): The description\n- [NoDesc](url2)\n"
    parsed = parse_llms_txt(raw)
    assert parsed.sections[0].links[0].title == "Link"
    assert parsed.sections[0].links[0].url == "url"
    assert parsed.sections[0].links[0].description == "The description"
    assert parsed.sections[0].links[1].description is None


def test_parse_no_headings() -> None:
    parsed = parse_llms_txt("just some text\nno headings here")
    assert parsed.title == ""
    assert parsed.sections == []
