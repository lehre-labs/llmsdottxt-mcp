"""VitePress platform detector."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from llmstxt_mcp.models import Platform
from llmstxt_mcp.platforms.base import BasePlatform

if TYPE_CHECKING:
    import httpx

    from llmstxt_mcp.models import PlatformHint


class VitePressPlatform(BasePlatform):
    """VitePress sites identified by generator meta tag or VP-specific DOM."""

    platform: ClassVar[Platform] = Platform.vitepress

    @override
    @classmethod
    def from_response(cls, response: httpx.Response, base: str) -> PlatformHint | None:
        body = response.text[:2000].lower() if response.text else ""
        if 'name="generator" content="vitepress' in body:
            return cls.hint(base, per_page=True)
        if any(marker in body for marker in ("vpcontent", "vpnav")):
            return cls.hint(base, per_page=True)
        return None
