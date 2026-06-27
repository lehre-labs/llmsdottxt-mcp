"""HTTP layer: transient retry, Retry-After, and bot-challenge handling."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from llmstxt_mcp import http
from llmstxt_mcp.errors import BlockedByChallengeError
from llmstxt_mcp.http import build_client

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

URL = "https://docs.example.com/llms.txt"


async def test_retries_429_then_succeeds(httpx_mock: HTTPXMock) -> None:
    """A genuine 429 is retried and the following 200 is returned."""
    httpx_mock.add_response(url=URL, status_code=429)
    httpx_mock.add_response(url=URL, status_code=200, text="ok")

    async with build_client() as client:
        response = await http.get(client, URL)

    assert response.status_code == 200
    assert response.text == "ok"
    assert len(httpx_mock.get_requests()) == 2


async def test_retries_503(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=URL, status_code=503)
    httpx_mock.add_response(url=URL, status_code=200, text="ok")

    async with build_client() as client:
        response = await http.get(client, URL)

    assert response.status_code == 200


async def test_gives_up_after_max_attempts(httpx_mock: HTTPXMock) -> None:
    """Persistent 429 exhausts retries and re-raises the transient error."""
    httpx_mock.add_response(url=URL, status_code=429)
    httpx_mock.add_response(url=URL, status_code=429)
    httpx_mock.add_response(url=URL, status_code=429)

    async with build_client() as client:
        with pytest.raises(http._TransientHTTPError):
            await http.get(client, URL)

    assert len(httpx_mock.get_requests()) == 3


async def test_cloudflare_challenge_is_not_retried(httpx_mock: HTTPXMock) -> None:
    """A Cloudflare challenge raises BlockedByChallengeError on the first hit."""
    httpx_mock.add_response(
        url=URL,
        status_code=429,
        headers={"cf-mitigated": "challenge", "server": "cloudflare"},
    )

    async with build_client() as client:
        with pytest.raises(BlockedByChallengeError) as excinfo:
            await http.get(client, URL)

    assert excinfo.value.vendor == "Cloudflare"
    assert excinfo.value.status_code == 429
    assert len(httpx_mock.get_requests()) == 1  # no wasted retries


async def test_cloudflare_challenge_on_403(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=URL, status_code=403, headers={"cf-mitigated": "managed_challenge"})

    async with build_client() as client:
        with pytest.raises(BlockedByChallengeError):
            await http.get(client, URL)

    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.parametrize(
    ("status", "headers", "vendor"),
    [
        (403, {"x-datadome": "protected"}, "DataDome"),
        (403, {"x-iinfo": "1-2-3"}, "Imperva Incapsula"),
        (403, {"x-amzn-waf-action": "captcha"}, "AWS WAF"),
        (403, {"server": "AkamaiGHost"}, "Akamai"),
        (403, {"server": "Sucuri/Cloudproxy"}, "Sucuri"),
    ],
)
async def test_other_wafs_are_detected(
    httpx_mock: HTTPXMock, status: int, headers: dict[str, str], vendor: str
) -> None:
    httpx_mock.add_response(url=URL, status_code=status, headers=headers)

    async with build_client() as client:
        with pytest.raises(BlockedByChallengeError) as excinfo:
            await http.get(client, URL)

    assert excinfo.value.vendor == vendor
    assert len(httpx_mock.get_requests()) == 1


async def test_plain_429_without_waf_header_retries(httpx_mock: HTTPXMock) -> None:
    """A genuine origin 429 (no WAF fingerprint) stays on the retry path."""
    httpx_mock.add_response(url=URL, status_code=429)
    httpx_mock.add_response(url=URL, status_code=200, text="ok")

    async with build_client() as client:
        response = await http.get(client, URL)

    assert response.status_code == 200
    assert len(httpx_mock.get_requests()) == 2


def test_retry_after_seconds_parses_and_caps() -> None:
    def resp(value: str) -> httpx.Response:
        return httpx.Response(429, headers={"retry-after": value})

    assert http._retry_after_seconds(resp("3")) == 3.0
    assert http._retry_after_seconds(resp("999")) == http._MAX_RETRY_AFTER
    # HTTP-date form is not numeric — fall back to exponential backoff.
    assert http._retry_after_seconds(resp("Wed, 21 Oct 2026 07:28:00 GMT")) is None
    assert http._retry_after_seconds(httpx.Response(429)) is None
