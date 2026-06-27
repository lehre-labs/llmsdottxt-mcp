"""Mintlify platform detector."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from llmstxt_mcp.config import MINTLIFY_HEADER, MINTLIFY_LINK_REL
from llmstxt_mcp.models import Platform
from llmstxt_mcp.platforms.base import BasePlatform

if TYPE_CHECKING:
    import httpx

    from llmstxt_mcp.models import PlatformHint


class MintlifyPlatform(BasePlatform):
    """Mintlify exposes an X-Llms-Txt header and a .well-known/llms.txt."""

    platform: ClassVar[Platform] = Platform.mintlify

    _HEADER_MARKERS = (MINTLIFY_HEADER, "x-mint-proxy-version", "x-mintlify-client-version")

    @override
    @classmethod
    def from_response(cls, response: httpx.Response, base: str) -> PlatformHint | None:
        headers = response.headers
        has_marker = any(headers.get(name) for name in cls._HEADER_MARKERS)
        if has_marker or f'rel="{MINTLIFY_LINK_REL}"' in headers.get("link", ""):
            return cls.hint(base, well_known=True, per_page=True, markdown_accept=True)
        return None

    @override
    @classmethod
    def from_url(cls, base_lower: str, base: str) -> PlatformHint | None:
        if ".mintlify." in base_lower:
            return cls.hint(base, well_known=True, per_page=True, markdown_accept=True)
        return None
