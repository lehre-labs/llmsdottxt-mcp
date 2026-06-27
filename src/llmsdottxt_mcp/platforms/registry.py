"""Platform detector registry, in priority order."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmsdottxt_mcp.config import LLMS_FULL_TXT_PATH, LLMS_TXT_PATH
from llmsdottxt_mcp.models import PlatformHint
from llmsdottxt_mcp.platforms.docusaurus import DocusaurusPlatform
from llmsdottxt_mcp.platforms.gitbook import GitBookPlatform
from llmsdottxt_mcp.platforms.github_pages import GitHubPagesPlatform
from llmsdottxt_mcp.platforms.mintlify import MintlifyPlatform
from llmsdottxt_mcp.platforms.mkdocs import MkDocsPlatform
from llmsdottxt_mcp.platforms.readme import ReadMePlatform
from llmsdottxt_mcp.platforms.readthedocs import ReadTheDocsPlatform
from llmsdottxt_mcp.platforms.redocly import RedoclyPlatform
from llmsdottxt_mcp.platforms.sphinx import SphinxPlatform
from llmsdottxt_mcp.platforms.starlight import StarlightPlatform
from llmsdottxt_mcp.platforms.vitepress import VitePressPlatform

if TYPE_CHECKING:
    from llmsdottxt_mcp.platforms.base import BasePlatform

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
