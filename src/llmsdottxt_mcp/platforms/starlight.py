"""Starlight (Astro) platform detector."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from llmsdottxt_mcp.models import Platform
from llmsdottxt_mcp.platforms.base import BasePlatform

if TYPE_CHECKING:
    import httpx

    from llmsdottxt_mcp.models import PlatformHint


class StarlightPlatform(BasePlatform):
    """Astro Starlight sites identified by --sl-* CSS custom properties or data attributes."""

    platform: ClassVar[Platform] = Platform.starlight

    @override
    @classmethod
    def from_response(cls, response: httpx.Response, base: str) -> PlatformHint | None:
        body = response.text[:2000].lower() if response.text else ""
        if "--sl-color" in body or "--sl-nav-height" in body:
            return cls.hint(base, per_page=True)
        if "data-starlight" in body or "starlight-toc" in body or "starlight-route" in body:
            return cls.hint(base, per_page=True)
        return None
