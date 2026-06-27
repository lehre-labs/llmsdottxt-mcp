"""Configuration: settings, constants, and logging."""

from __future__ import annotations

from llmstxt_mcp.config.constants import (
    BLOCKING_HTTP_STATUSES,
    DEFAULT_MCP_HOST,
    DEFAULT_MCP_PORT,
    GO_FORGE_HOSTS,
    LLMS_FULL_TXT_PATH,
    LLMS_TXT_PATH,
    MAX_RETRY_AFTER_SECONDS,
    MINTLIFY_HEADER,
    MINTLIFY_LINK_REL,
    PYTHON_SKIP_PACKAGE_NAMES,
    RETRYABLE_HTTP_STATUSES,
    STREAM_CHUNK_SIZE,
    USER_AGENT,
    WAF_HEADER_FINGERPRINTS,
    WELL_KNOWN_LLMS,
    WELL_KNOWN_LLMS_FULL,
)
from llmstxt_mcp.config.logging import configure_logging
from llmstxt_mcp.config.settings import Settings, settings

__all__ = [
    "BLOCKING_HTTP_STATUSES",
    "DEFAULT_MCP_HOST",
    "DEFAULT_MCP_PORT",
    "GO_FORGE_HOSTS",
    "LLMS_FULL_TXT_PATH",
    "LLMS_TXT_PATH",
    "MAX_RETRY_AFTER_SECONDS",
    "MINTLIFY_HEADER",
    "MINTLIFY_LINK_REL",
    "PYTHON_SKIP_PACKAGE_NAMES",
    "RETRYABLE_HTTP_STATUSES",
    "STREAM_CHUNK_SIZE",
    "USER_AGENT",
    "WAF_HEADER_FINGERPRINTS",
    "WELL_KNOWN_LLMS",
    "WELL_KNOWN_LLMS_FULL",
    "Settings",
    "configure_logging",
    "settings",
]
