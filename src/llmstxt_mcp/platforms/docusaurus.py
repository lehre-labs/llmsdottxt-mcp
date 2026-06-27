"""Docusaurus platform detector."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from llmstxt_mcp.models import Platform
from llmstxt_mcp.platforms.base import BasePlatform

if TYPE_CHECKING:
    import httpx

    from llmstxt_mcp.models import PlatformHint


class DocusaurusPlatform(BasePlatform):
    """Docusaurus sites are identified by a marker in the page body."""

    platform: ClassVar[Platform] = Platform.docusaurus

    @override
    @classmethod
    def from_response(cls, response: httpx.Response, base: str) -> PlatformHint | None:
        body = response.text[:2000].lower() if response.text else ""
        if "docusaurus" in body:
            return cls.hint(base, per_page=True)
        return None
