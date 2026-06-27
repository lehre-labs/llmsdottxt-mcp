"""Read the Docs platform detector."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from llmstxt_mcp.models import Platform
from llmstxt_mcp.platforms.base import BasePlatform

if TYPE_CHECKING:
    import httpx

    from llmstxt_mcp.models import PlatformHint


class ReadTheDocsPlatform(BasePlatform):
    """Read the Docs sites are identified by host or page body."""

    platform: ClassVar[Platform] = Platform.readthedocs

    @override
    @classmethod
    def from_response(cls, response: httpx.Response, base: str) -> PlatformHint | None:
        body = response.text[:2000].lower() if response.text else ""
        if "read the docs" in body:
            return cls.hint(base, per_page=True)
        return None

    @override
    @classmethod
    def from_url(cls, base_lower: str, base: str) -> PlatformHint | None:
        if any(host in base_lower for host in ("readthedocs.io", "rtfd.io")):
            return cls.hint(base, per_page=True)
        return None
