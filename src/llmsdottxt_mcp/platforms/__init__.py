"""Documentation platform detection.

Add a platform by dropping a ``BasePlatform`` subclass in this package and
registering it in ``registry.PLATFORM_REGISTRY``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import structlog

from llmsdottxt_mcp import http
from llmsdottxt_mcp.platforms.base import BasePlatform
from llmsdottxt_mcp.platforms.registry import PLATFORM_REGISTRY, default_hint

if TYPE_CHECKING:
    from llmsdottxt_mcp.models import PlatformHint

logger = structlog.get_logger(__name__)


async def detect_platform(docs_base_url: str, client: httpx.AsyncClient) -> PlatformHint:
    """Detect the platform from the docs homepage headers/body, then URL heuristics.

    Platform fingerprints (e.g. Mintlify's ``x-llms-txt`` header) live on the docs
    homepage, not on the plain-text ``/llms.txt`` endpoint, so we probe the base URL.
    """
    base = docs_base_url.rstrip("/")

    try:
        response = await http.get(client, base or docs_base_url)
        if response.status_code == 200:
            for platform in PLATFORM_REGISTRY:
                if hint := platform.from_response(response, base):
                    return hint
    except httpx.HTTPError as exc:
        logger.debug("platform_probe_failed", url=base, error=str(exc))

    base_lower = docs_base_url.lower()
    for platform in PLATFORM_REGISTRY:
        if hint := platform.from_url(base_lower, base):
            return hint
    return default_hint(base)


__all__ = ["PLATFORM_REGISTRY", "BasePlatform", "default_hint", "detect_platform"]
