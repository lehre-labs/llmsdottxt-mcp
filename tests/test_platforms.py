"""Platform detection tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from llmsdottxt_mcp.http import build_client
from llmsdottxt_mcp.models import Platform
from llmsdottxt_mcp.platforms import detect_platform

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


async def test_detect_mintlify_llms_header(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://docs.example.com",
        status_code=200,
        html="<html></html>",
        headers={"x-llms-txt": "/llms.txt"},
    )
    async with build_client() as client:
        hint = await detect_platform("https://docs.example.com", client)
    assert hint.platform == Platform.mintlify
    assert any("/.well-known/llms.txt" in u for u in hint.llms_txt_urls)
    assert hint.headers.get("Accept") == "text/markdown"


async def test_detect_mintlify_proxy_header(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://gofastmcp.com",
        status_code=200,
        html="<html></html>",
        headers={"x-mint-proxy-version": "1.0.0-prod"},
    )
    async with build_client() as client:
        hint = await detect_platform("https://gofastmcp.com", client)
    assert hint.platform == Platform.mintlify


async def test_detect_readthedocs_from_url(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://foo.readthedocs.io", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://foo.readthedocs.io", client)
    assert hint.platform == Platform.readthedocs
    assert hint.per_page_md_pattern == "{base_url}{path}.md"


async def test_detect_gitbook_from_url(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://myproject.gitbook.io", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://myproject.gitbook.io", client)
    assert hint.platform == Platform.gitbook
    assert hint.per_page_md_pattern == "{base_url}{path}.md"


async def test_detect_gitbook_from_body(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://docs.acme.com",
        status_code=200,
        html='<html><head><script src="gitbook/theme.js"></script></head></html>',
    )
    async with build_client() as client:
        hint = await detect_platform("https://docs.acme.com", client)
    assert hint.platform == Platform.gitbook


async def test_detect_mkdocs_from_generator_meta(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://docs.acme.com",
        status_code=200,
        html='<html><head><meta name="generator" content="mkdocs-1.6.0"></head></html>',
    )
    async with build_client() as client:
        hint = await detect_platform("https://docs.acme.com", client)
    assert hint.platform == Platform.mkdocs


async def test_detect_mkdocs_from_body_marker(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://docs.acme.com",
        status_code=200,
        html='<html><head><link href="mkdocs/styles.css"></head></html>',
    )
    async with build_client() as client:
        hint = await detect_platform("https://docs.acme.com", client)
    assert hint.platform == Platform.mkdocs


async def test_detect_readme_from_url(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://myproject.readme.io", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://myproject.readme.io", client)
    assert hint.platform == Platform.readme
    assert hint.per_page_md_pattern == "{base_url}{path}.md"


async def test_detect_readme_from_variant_domain(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api-docs.acme.readme.io", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://api-docs.acme.readme.io", client)
    assert hint.platform == Platform.readme


async def test_detect_redocly_from_url(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api-docs.redoc.ly", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://api-docs.redoc.ly", client)
    assert hint.platform == Platform.redocly


async def test_detect_redocly_from_subdomain(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://docs.redoc.ly", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://docs.redoc.ly", client)
    assert hint.platform == Platform.redocly


async def test_detect_default_unknown(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://example.com", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://example.com", client)
    assert hint.platform is None


# ---------------------------------------------------------------------------
# VitePress
# ---------------------------------------------------------------------------


async def test_detect_vitepress_generator_meta(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://vitepress.dev",
        status_code=200,
        html='<html><head><meta name="generator" content="VitePress v1.5.0"></head></html>',
    )
    async with build_client() as client:
        hint = await detect_platform("https://vitepress.dev", client)
    assert hint.platform == Platform.vitepress
    assert hint.per_page_md_pattern == "{base_url}{path}.md"


async def test_detect_vitepress_vpcontent(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://vuejs.org",
        status_code=200,
        html="<html><body><div id='VPContent'><nav class='VPNav'>Docs</nav></div></body></html>",
    )
    async with build_client() as client:
        hint = await detect_platform("https://vuejs.org", client)
    assert hint.platform == Platform.vitepress


async def test_detect_vitepress_no_match(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://other-vue-site.com",
        status_code=200,
        html="<html><body><div id='app'>Hello</div></body></html>",
    )
    async with build_client() as client:
        hint = await detect_platform("https://other-vue-site.com", client)
    assert hint.platform is None


# ---------------------------------------------------------------------------
# Starlight
# ---------------------------------------------------------------------------


async def test_detect_starlight_css_vars(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://starlight.astro.build",
        status_code=200,
        html="<html><head><style>:root { --sl-color-accent: #007bff; --sl-nav-height: 3.5rem; }</style></head></html>",
    )
    async with build_client() as client:
        hint = await detect_platform("https://starlight.astro.build", client)
    assert hint.platform == Platform.starlight
    assert hint.per_page_md_pattern == "{base_url}{path}.md"


async def test_detect_starlight_data_attr(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://docs.astro.build",
        status_code=200,
        html='<html lang="en" data-starlight-theme="dark"><body><starlight-toc></starlight-toc></body></html>',
    )
    async with build_client() as client:
        hint = await detect_platform("https://docs.astro.build", client)
    assert hint.platform == Platform.starlight


async def test_detect_starlight_no_match(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://other-astro-site.com",
        status_code=200,
        html="<html><body><div id='app'>Hello</div></body></html>",
    )
    async with build_client() as client:
        hint = await detect_platform("https://other-astro-site.com", client)
    assert hint.platform is None


# ---------------------------------------------------------------------------
# Sphinx
# ---------------------------------------------------------------------------


async def test_detect_sphinx_generator_meta(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://docs.sqlalchemy.org",
        status_code=200,
        html='<html><head><meta name="generator" content="Sphinx 7.4.7"></head></html>',
    )
    async with build_client() as client:
        hint = await detect_platform("https://docs.sqlalchemy.org", client)
    assert hint.platform == Platform.sphinx


async def test_detect_sphinx_static_assets(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://docs.celeryproject.org",
        status_code=200,
        html='<html><head><link rel="stylesheet" href="_static/pygments.css"><script src="_static/documentation_options.js"></script></head></html>',
    )
    async with build_client() as client:
        hint = await detect_platform("https://docs.celeryproject.org", client)
    assert hint.platform == Platform.sphinx


async def test_detect_sphinx_no_match(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://other-python-docs.com",
        status_code=200,
        html="<html><head><link rel='stylesheet' href='/static/pygments.css'></head></html>",
    )
    async with build_client() as client:
        hint = await detect_platform("https://other-python-docs.com", client)
    assert hint.platform is None
    assert hint.llms_txt_urls == ["https://other-python-docs.com/llms.txt"]


async def test_detect_mintlify_url(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://docs.mintlify.app", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://docs.mintlify.app", client)
    assert hint.platform == Platform.mintlify


async def test_detect_docusaurus_no_match(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://unknown-site.com",
        status_code=200,
        html="<html><body>just a regular site</body></html>",
    )
    async with build_client() as client:
        hint = await detect_platform("https://unknown-site.com", client)
    assert hint.platform is None


async def test_detect_docusaurus_body(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://docusaurus.io",
        status_code=200,
        html='<html><script src="/assets/js/runtime~main.docusaurus.js"></script></html>',
    )
    async with build_client() as client:
        hint = await detect_platform("https://docusaurus.io", client)
    assert hint.platform == Platform.docusaurus


async def test_detect_readthedocs_body(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://custom-docs.example.com",
        status_code=200,
        html="<html><footer>Powered by Read the Docs</footer></html>",
    )
    async with build_client() as client:
        hint = await detect_platform("https://custom-docs.example.com", client)
    assert hint.platform == Platform.readthedocs


async def test_detect_readthedocs_rtfd(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://myproject.rtfd.io", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://myproject.rtfd.io", client)
    assert hint.platform == Platform.readthedocs


async def test_detect_github_pages_no_match(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://not-gh-pages.example.com", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://not-gh-pages.example.com", client)
    assert hint.platform is None


async def test_detect_github_pages_url(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://my-org.github.io/repo", status_code=404)
    async with build_client() as client:
        hint = await detect_platform("https://my-org.github.io/repo", client)
    assert hint.platform == Platform.github_pages


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_detect_platform_probe_http_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(
        url="https://down.example.com", exception=httpx.ConnectError("refused")
    )
    async with build_client() as client:
        hint = await detect_platform("https://down.example.com", client)
    assert hint.platform is None
