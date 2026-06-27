"""GitBook platform detector."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from llmsdottxt_mcp.models import Platform
from llmsdottxt_mcp.platforms.base import BasePlatform

if TYPE_CHECKING:
    import httpx

    from llmsdottxt_mcp.models import PlatformHint


class GitBookPlatform(BasePlatform):
    """GitBook-hosted documentation. Supports per-page .md retrieval."""

    platform: ClassVar[Platform] = Platform.gitbook

    @override
    @classmethod
    def from_response(cls, response: httpx.Response, base: str) -> PlatformHint | None:
        body = response.text[:2000].lower() if response.text else ""
        if "gitbook" in body:
            return cls.hint(base, per_page=True, markdown_accept=True)
        return None

    @override
    @classmethod
    def from_url(cls, base_lower: str, base: str) -> PlatformHint | None:
        if ".gitbook.io" in base_lower:
            return cls.hint(base, per_page=True, markdown_accept=True)
        return None
