"""Shared async HTTP client with retry and rate-limit protection."""

from __future__ import annotations

from asyncio import AbstractEventLoop, get_running_loop
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from aiolimiter import AsyncLimiter
import httpx
import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from llmsdottxt_mcp.config import (
    BLOCKING_HTTP_STATUSES,
    MAX_RETRY_AFTER_SECONDS,
    RETRYABLE_HTTP_STATUSES,
    USER_AGENT,
    WAF_HEADER_FINGERPRINTS,
    settings,
)
from llmsdottxt_mcp.errors import BlockedByChallengeError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from tenacity import RetryCallState

logger = structlog.get_logger(__name__)

_limiters: WeakKeyDictionary[AbstractEventLoop, AsyncLimiter] = WeakKeyDictionary()


class _TransientHTTPError(Exception):
    """Raised for retryable HTTP responses (5xx, 429, 503)."""

    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        super().__init__(f"Retryable HTTP {response.status_code}")


def _challenge_vendor(response: httpx.Response) -> str | None:
    """Return the bot-wall vendor if ``response`` is an unsolvable challenge, else None.

    Cloudflare's ``cf-mitigated`` header is authoritative -- present only when CF
    actively challenged/blocked the request. Other WAFs are matched by their
    dedicated header on a blocking status, which keeps genuine origin 429/503
    rate limits (no such header) on the retry path.
    """
    # Cloudflare: authoritative, status-independent.
    if response.headers.get("cf-mitigated", "").lower() not in {"", "ok", "response"}:
        return "Cloudflare"
    if response.status_code not in BLOCKING_HTTP_STATUSES:
        return None
    for header, vendor in WAF_HEADER_FINGERPRINTS:
        if header in response.headers:
            return vendor
    # Akamai / Sucuri identify via the Server banner on a block.
    server = response.headers.get("server", "").lower()
    if "akamaighost" in server:
        return "Akamai"
    if "sucuri" in server:
        return "Sucuri"
    return None


def _retry_after_seconds(response: httpx.Response) -> float | None:
    """Parse a numeric ``Retry-After`` header, capped; ignore HTTP-date form."""
    raw = response.headers.get("retry-after")
    if not raw:
        return None
    try:
        return min(float(raw), MAX_RETRY_AFTER_SECONDS)
    except ValueError:
        return None  # HTTP-date form -- fall back to exponential backoff


_EXPONENTIAL = wait_exponential(multiplier=0.5, min=0.5, max=5)


def _wait(retry_state: RetryCallState) -> float:
    """Honor a server ``Retry-After`` when present, else exponential backoff."""
    outcome = retry_state.outcome
    exc = outcome.exception() if outcome else None
    if isinstance(exc, _TransientHTTPError):
        after = _retry_after_seconds(exc.response)
        if after is not None:
            return after
    return _EXPONENTIAL(retry_state)


def build_client(timeout: float | None = None) -> httpx.AsyncClient:
    """Create an AsyncClient with the shared User-Agent and redirect policy."""
    return httpx.AsyncClient(
        timeout=httpx.Timeout(timeout or settings.http_timeout),
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    )


def _limiter() -> AsyncLimiter:
    """Return a per-event-loop rate limiter."""
    loop = get_running_loop()
    limiter = _limiters.get(loop)
    if limiter is None:
        limiter = AsyncLimiter(settings.rate_limit_per_minute, 60)
        _limiters[loop] = limiter
    return limiter


@retry(
    stop=stop_after_attempt(3),
    wait=_wait,
    retry=retry_if_exception_type(
        (httpx.ConnectError, httpx.TimeoutException, _TransientHTTPError)
    ),
    reraise=True,
)
async def get(
    client: httpx.AsyncClient,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float | None = None,
) -> httpx.Response:
    """Rate-limited GET that retries transient errors and surfaces bot challenges.

    Raises ``BlockedByChallengeError`` (non-retryable) when a host serves an
    unsolvable bot wall, so callers skip it instead of burning retries.
    """
    async with _limiter():
        response = await client.get(url, headers=headers, timeout=timeout)
    vendor = _challenge_vendor(response)
    if vendor is not None:
        raise BlockedByChallengeError(url, response.status_code, vendor=vendor)
    if response.status_code >= 500 or response.status_code in RETRYABLE_HTTP_STATUSES:
        raise _TransientHTTPError(response)
    return response


@asynccontextmanager
async def stream(
    client: httpx.AsyncClient,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float | None = None,
) -> AsyncGenerator[httpx.Response]:
    """Rate-limited streaming GET context manager (no retry -- body is consumed once)."""
    async with _limiter(), client.stream("GET", url, headers=headers, timeout=timeout) as response:
        yield response
