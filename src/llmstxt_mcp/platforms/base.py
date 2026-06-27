"""Base platform detector interface and shared hint builder."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from llmstxt_mcp.config import (
    LLMS_FULL_TXT_PATH,
    LLMS_TXT_PATH,
    WELL_KNOWN_LLMS,
    WELL_KNOWN_LLMS_FULL,
)
from llmstxt_mcp.models import PlatformHint

if TYPE_CHECKING:
    import httpx

    from llmstxt_mcp.models import Platform


class BasePlatform:
    """Detects a documentation platform from a probe response or its URL.

    Subclasses override :meth:`from_response` and/or :meth:`from_url`.
    """

    platform: ClassVar[Platform]

    @classmethod
    def from_response(cls, response: httpx.Response, base: str) -> PlatformHint | None:
        """Detect from a successful /llms.txt probe (headers/body). Default: no match."""
        return None

    @classmethod
    def from_url(cls, base_lower: str, base: str) -> PlatformHint | None:
        """Detect from the docs base URL alone. Default: no match."""
        return None

    @classmethod
    def hint(
        cls,
        base: str,
        *,
        well_known: bool = False,
        per_page: bool = False,
        markdown_accept: bool = False,
    ) -> PlatformHint:
        """Build a PlatformHint with prioritized URLs for this platform."""
        if well_known:
            llms = [base + WELL_KNOWN_LLMS, base + LLMS_TXT_PATH]
            full = [base + WELL_KNOWN_LLMS_FULL, base + LLMS_FULL_TXT_PATH]
        else:
            llms = [base + LLMS_TXT_PATH]
            full = [base + LLMS_FULL_TXT_PATH]
        return PlatformHint(
            platform=cls.platform,
            llms_txt_urls=llms,
            llms_full_txt_urls=full,
            per_page_md_pattern="{base_url}{path}.md" if per_page else None,
            headers={"Accept": "text/markdown"} if markdown_accept else {},
        )
