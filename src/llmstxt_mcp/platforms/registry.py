"""Platform detector registry, in priority order."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmstxt_mcp.config import LLMS_FULL_TXT_PATH, LLMS_TXT_PATH
from llmstxt_mcp.models import PlatformHint
from llmstxt_mcp.platforms.docusaurus import DocusaurusPlatform
from llmstxt_mcp.platforms.gitbook import GitBookPlatform
from llmstxt_mcp.platforms.github_pages import GitHubPagesPlatform
from llmstxt_mcp.platforms.mintlify import MintlifyPlatform
from llmstxt_mcp.platforms.mkdocs import MkDocsPlatform
from llmstxt_mcp.platforms.readme import ReadMePlatform
from llmstxt_mcp.platforms.readthedocs import ReadTheDocsPlatform
from llmstxt_mcp.platforms.redocly import RedoclyPlatform
from llmstxt_mcp.platforms.sphinx import SphinxPlatform
from llmstxt_mcp.platforms.starlight import StarlightPlatform
from llmstxt_mcp.platforms.vitepress import VitePressPlatform

if TYPE_CHECKING:
    from llmstxt_mcp.platforms.base import BasePlatform

PLATFORM_REGISTRY: list[type[BasePlatform]] = [
    MintlifyPlatform,
    ReadTheDocsPlatform,
    ReadMePlatform,
    DocusaurusPlatform,
    GitBookPlatform,
    RedoclyPlatform,
    MkDocsPlatform,
    SphinxPlatform,
    VitePressPlatform,
    StarlightPlatform,
    GitHubPagesPlatform,
]


def default_hint(base: str) -> PlatformHint:
    """Fallback hint using the standard llms.txt paths."""
    return PlatformHint(
        platform=None,
        llms_txt_urls=[base + LLMS_TXT_PATH],
        llms_full_txt_urls=[base + LLMS_FULL_TXT_PATH],
    )
