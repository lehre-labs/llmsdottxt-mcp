"""Configuration: settings, constants, and logging."""

from __future__ import annotations

from llmstxt_mcp.config.constants import (
    GO_FORGE_HOSTS,
    LLMS_FULL_TXT_PATH,
    LLMS_TXT_PATH,
    MINTLIFY_HEADER,
    MINTLIFY_LINK_REL,
    STREAM_CHUNK_SIZE,
    USER_AGENT,
    WELL_KNOWN_LLMS,
    WELL_KNOWN_LLMS_FULL,
)
from llmstxt_mcp.config.logging import configure_logging
from llmstxt_mcp.config.settings import Settings, settings

__all__ = [
    "GO_FORGE_HOSTS",
    "LLMS_FULL_TXT_PATH",
    "LLMS_TXT_PATH",
    "MINTLIFY_HEADER",
    "MINTLIFY_LINK_REL",
    "STREAM_CHUNK_SIZE",
    "USER_AGENT",
    "WELL_KNOWN_LLMS",
    "WELL_KNOWN_LLMS_FULL",
    "Settings",
    "configure_logging",
    "settings",
]
