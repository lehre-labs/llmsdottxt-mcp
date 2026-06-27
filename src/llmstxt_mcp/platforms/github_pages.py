"""GitHub Pages platform detector."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from llmstxt_mcp.models import Platform
from llmstxt_mcp.platforms.base import BasePlatform

if TYPE_CHECKING:
    from llmstxt_mcp.models import PlatformHint


class GitHubPagesPlatform(BasePlatform):
    """github.io-hosted documentation."""

    platform: ClassVar[Platform] = Platform.github_pages

    @override
    @classmethod
    def from_url(cls, base_lower: str, base: str) -> PlatformHint | None:
        if "github.io" in base_lower:
            return cls.hint(base)
        return None
