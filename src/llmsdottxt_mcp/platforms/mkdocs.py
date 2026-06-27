"""MkDocs platform detector."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from llmsdottxt_mcp.models import Platform
from llmsdottxt_mcp.platforms.base import BasePlatform

if TYPE_CHECKING:
    import httpx

    from llmsdottxt_mcp.models import PlatformHint


class MkDocsPlatform(BasePlatform):
    """MkDocs (including Material theme) sites."""

    platform: ClassVar[Platform] = Platform.mkdocs

    @override
    @classmethod
    def from_response(cls, response: httpx.Response, base: str) -> PlatformHint | None:
        body = response.text[:2000].lower() if response.text else ""
        if "mkdocs" in body:
            return cls.hint(base)
        return None
