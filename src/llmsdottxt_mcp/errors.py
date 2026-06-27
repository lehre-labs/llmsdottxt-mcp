"""Typed error hierarchy for the llmsdottxt-mcp internals.

Lower layers raise these; the tool boundary translates them into FastMCP
``ToolError`` so agents receive clean, actionable messages.
"""

from __future__ import annotations


class LlmstxtError(Exception):
    """Base class for all llmsdottxt-mcp domain errors."""


class ResolveError(LlmstxtError):
    """A package could not be resolved to a documentation URL."""


class FetchError(LlmstxtError):
    """An llms.txt resource could not be fetched."""


class BlockedByChallengeError(LlmstxtError):
    """A docs host served a bot challenge (e.g. Cloudflare) we cannot solve headlessly.

    Distinct from a genuine rate limit: retrying with the same headless client will
    never succeed, so callers should record this as *blocked* rather than *missing*
    and stop probing that host.
    """

    def __init__(self, url: str, status_code: int, *, vendor: str = "bot challenge") -> None:
        self.url = url
        self.status_code = status_code
        self.vendor = vendor
        super().__init__(
            f"Blocked by {vendor} (HTTP {status_code}) at {url}. "
            "This host requires a browser to pass; skipping."
        )


class PackageNotIndexedError(LlmstxtError):
    """A requested package is not present in the local index."""

    def __init__(self, package: str) -> None:
        self.package = package
        super().__init__(f"Package '{package}' is not indexed. Run index_deps first.")
