"""Protocol-level constants for the llms.txt convention."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

LLMS_TXT_PATH = "/llms.txt"
LLMS_FULL_TXT_PATH = "/llms-full.txt"
WELL_KNOWN_LLMS = "/.well-known/llms.txt"
WELL_KNOWN_LLMS_FULL = "/.well-known/llms-full.txt"

MINTLIFY_HEADER = "X-Llms-Txt"
MINTLIFY_LINK_REL = "llms-txt"

STREAM_CHUNK_SIZE = 64 * 1024  # 64 KB

try:
    _VERSION = version("llmstxt-mcp")
except PackageNotFoundError:  # pragma: no cover - editable installs without metadata
    _VERSION = "0.0.0"

USER_AGENT = f"llmstxt-mcp/{_VERSION}"
