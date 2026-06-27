"""Resolver tests (PyPI JSON API mocked)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from llmsdottxt_mcp.http import build_client
from llmsdottxt_mcp.models import DocsUrlSource, Ecosystem
from llmsdottxt_mcp.resolvers import resolve

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


async def test_resolve_documentation_url(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://pypi.org/pypi/requests/json",
        json={
            "info": {
                "version": "2.32.3",
                "home_page": "https://requests.readthedocs.io",
                "project_urls": {
                    "Documentation": "https://requests.readthedocs.io/",
                    "Source": "https://github.com/psf/requests",
                },
            }
        },
    )
    async with build_client() as client:
        info = await resolve("requests", Ecosystem.python, client)

    assert info is not None
    assert info.docs_base_url == "https://requests.readthedocs.io"
    assert info.docs_url_source == DocsUrlSource.pypi_project_urls
    assert info.repository_url == "https://github.com/psf/requests"
    assert info.latest_version == "2.32.3"


async def test_resolve_homepage_fallback(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://pypi.org/pypi/lib/json",
        json={
            "info": {"version": "1.0", "home_page": "https://lib.example.com", "project_urls": {}}
        },
    )
    async with build_client() as client:
        info = await resolve("lib", Ecosystem.python, client)

    assert info is not None
    assert info.docs_base_url == "https://lib.example.com"
    assert info.docs_url_source == DocsUrlSource.homepage_fallback


async def test_resolve_missing_package(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://pypi.org/pypi/nope/json", status_code=404)
    async with build_client() as client:
        assert await resolve("nope", Ecosystem.python, client) is None


async def test_resolve_npm(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://registry.npmjs.org/react/latest",
        json={
            "version": "18.3.1",
            "homepage": "https://react.dev/",
            "repository": {"type": "git", "url": "git+https://github.com/facebook/react.git"},
        },
    )
    async with build_client() as client:
        info = await resolve("react", Ecosystem.node, client)

    assert info is not None
    assert info.docs_base_url == "https://react.dev"
    assert info.docs_url_source == DocsUrlSource.homepage_fallback
    assert info.repository_url == "https://github.com/facebook/react"
    assert info.latest_version == "18.3.1"


async def test_resolve_crates(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://crates.io/api/v1/crates/serde",
        json={
            "crate": {
                "documentation": "https://docs.rs/serde/",
                "homepage": "https://serde.rs",
                "repository": "https://github.com/serde-rs/serde",
                "max_stable_version": "1.0.203",
                "newest_version": "1.0.204",
            }
        },
    )
    async with build_client() as client:
        info = await resolve("serde", Ecosystem.rust, client)

    assert info is not None
    assert info.docs_base_url == "https://docs.rs/serde"
    assert info.docs_url_source == DocsUrlSource.registry_documentation
    assert info.latest_version == "1.0.203"


async def test_resolve_go(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://proxy.golang.org/github.com/gin-gonic/gin/@latest",
        json={"Version": "v1.9.1", "Time": "2023-06-22T00:00:00Z"},
    )
    async with build_client() as client:
        info = await resolve("github.com/gin-gonic/gin", Ecosystem.go, client)

    assert info is not None
    assert info.docs_base_url == "https://pkg.go.dev/github.com/gin-gonic/gin"
    assert info.docs_url_source == DocsUrlSource.registry_documentation
    assert info.repository_url == "https://github.com/gin-gonic/gin"
    assert info.latest_version == "v1.9.1"


async def test_resolve_go_case_encoded(httpx_mock: HTTPXMock) -> None:
    """Uppercase module paths are case-encoded for the proxy (Azure -> !azure)."""
    httpx_mock.add_response(
        url="https://proxy.golang.org/github.com/!azure/azure-sdk-for-go/@latest",
        json={"Version": "v68.0.0"},
    )
    async with build_client() as client:
        info = await resolve("github.com/Azure/azure-sdk-for-go", Ecosystem.go, client)

    assert info is not None
    assert info.latest_version == "v68.0.0"


async def test_resolve_go_unknown_module(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://proxy.golang.org/example.com/nope/@latest", status_code=404
    )
    async with build_client() as client:
        assert await resolve("example.com/nope", Ecosystem.go, client) is None


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_resolve_pypi_http_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(
        url="https://pypi.org/pypi/broken/json",
        exception=httpx.ConnectError("refused"),
    )
    async with build_client() as client:
        assert await resolve("broken", Ecosystem.python, client) is None


async def test_resolve_pypi_invalid_json(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://pypi.org/pypi/bad/json", text="not json")
    async with build_client() as client:
        assert await resolve("bad", Ecosystem.python, client) is None


async def test_resolve_pypi_no_docs(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://pypi.org/pypi/nodocs/json",
        json={"info": {"version": "1.0", "project_urls": {}}},
    )
    async with build_client() as client:
        info = await resolve("nodocs", Ecosystem.python, client)
    assert info is not None
    assert info.docs_base_url is None
    assert info.docs_url_source == DocsUrlSource.none


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_resolve_npm_http_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(
        url="https://registry.npmjs.org/broken/latest", exception=httpx.ConnectError("refused")
    )
    async with build_client() as client:
        assert await resolve("broken", Ecosystem.node, client) is None


async def test_resolve_npm_no_homepage(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://registry.npmjs.org/nodocs/latest",
        json={"version": "2.0", "repository": {"url": "git+https://github.com/x/y.git"}},
    )
    async with build_client() as client:
        info = await resolve("nodocs", Ecosystem.node, client)
    assert info is not None
    assert info.docs_base_url is None
    assert info.docs_url_source == DocsUrlSource.none


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_resolve_crates_http_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(
        url="https://crates.io/api/v1/crates/broken", exception=httpx.ConnectError("refused")
    )
    async with build_client() as client:
        assert await resolve("broken", Ecosystem.rust, client) is None


async def test_resolve_crates_homepage_fallback(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://crates.io/api/v1/crates/lib",
        json={
            "crate": {
                "homepage": "https://lib.rs/",
                "repository": "https://github.com/foo/lib",
                "max_stable_version": "2.0.0",
            }
        },
    )
    async with build_client() as client:
        info = await resolve("lib", Ecosystem.rust, client)
    assert info is not None
    assert info.docs_base_url == "https://lib.rs"
    assert info.docs_url_source == DocsUrlSource.registry_documentation


async def test_resolve_crates_no_docs(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://crates.io/api/v1/crates/nodocs",
        json={"crate": {"repository": "https://github.com/foo/nodocs", "newest_version": "0.1"}},
    )
    async with build_client() as client:
        info = await resolve("nodocs", Ecosystem.rust, client)
    assert info is not None
    assert info.docs_base_url is None
    assert info.docs_url_source == DocsUrlSource.none


@pytest.mark.httpx_mock(
    can_send_already_matched_responses=True, assert_all_responses_were_requested=False
)
async def test_resolve_go_http_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(
        url="https://proxy.golang.org/github.com/x/y/@latest",
        exception=httpx.ConnectError("refused"),
    )
    async with build_client() as client:
        assert await resolve("github.com/x/y", Ecosystem.go, client) is None


async def test_resolve_npm_not_found(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://registry.npmjs.org/nope/latest", status_code=404)
    async with build_client() as client:
        assert await resolve("nope", Ecosystem.node, client) is None


async def test_resolve_npm_no_repository(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://registry.npmjs.org/lonely/latest",
        json={"version": "1.0.0", "homepage": "https://lonely.dev"},
    )
    async with build_client() as client:
        info = await resolve("lonely", Ecosystem.node, client)
    assert info is not None
    assert info.repository_url is None
    assert info.docs_base_url == "https://lonely.dev"


async def test_resolve_npm_string_repository(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://registry.npmjs.org/strrepo/latest",
        json={"version": "1.0.0", "repository": "git+https://github.com/o/strrepo.git"},
    )
    async with build_client() as client:
        info = await resolve("strrepo", Ecosystem.node, client)
    assert info is not None
    assert info.repository_url == "https://github.com/o/strrepo"


async def test_resolve_crates_not_found(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://crates.io/api/v1/crates/nope", status_code=404)
    async with build_client() as client:
        assert await resolve("nope", Ecosystem.rust, client) is None
