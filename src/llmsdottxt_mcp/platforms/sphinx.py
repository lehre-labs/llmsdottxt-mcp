"""Sphinx platform detector."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from llmsdottxt_mcp.models import Platform
from llmsdottxt_mcp.platforms.base import BasePlatform

if TYPE_CHECKING:
    import httpx

    from llmsdottxt_mcp.models import PlatformHint


class SphinxPlatform(BasePlatform):
    """Sphinx sites identified by generator meta or _static path patterns."""

    platform: ClassVar[Platform] = Platform.sphinx

    @override
    @classmethod
    def from_response(cls, response: httpx.Response, base: str) -> PlatformHint | None:
        body = response.text[:2000].lower() if response.text else ""
        if 'name="generator" content="sphinx' in body:
            return cls.hint(base)
        if "_static/pygments.css" in body or "_static/documentation_options.js" in body:
            return cls.hint(base)
        return None
