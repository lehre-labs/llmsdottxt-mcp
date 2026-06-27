"""ReadMe platform detector."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from llmsdottxt_mcp.models import Platform
from llmsdottxt_mcp.platforms.base import BasePlatform

if TYPE_CHECKING:
    from llmsdottxt_mcp.models import PlatformHint


class ReadMePlatform(BasePlatform):
    """ReadMe-hosted documentation. LLMs.txt is toggle-gated; serves per-page .md."""

    platform: ClassVar[Platform] = Platform.readme

    @override
    @classmethod
    def from_url(cls, base_lower: str, base: str) -> PlatformHint | None:
        if ".readme.io" in base_lower:
            return cls.hint(base, per_page=True)
        return None
