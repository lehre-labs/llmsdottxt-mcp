"""Protocol-level constants for the llms.txt convention."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

# -- llms.txt protocol paths ---------------------------------------------------
LLMS_TXT_PATH = "/llms.txt"
LLMS_FULL_TXT_PATH = "/llms-full.txt"
WELL_KNOWN_LLMS = "/.well-known/llms.txt"
WELL_KNOWN_LLMS_FULL = "/.well-known/llms-full.txt"

# -- llms.txt protocol headers -------------------------------------------------
MINTLIFY_HEADER = "X-Llms-Txt"
MINTLIFY_LINK_REL = "llms-txt"

# -- HTTP client ---------------------------------------------------------------
STREAM_CHUNK_SIZE = 64 * 1024  # 64 KB

# Statuses worth retrying: 5xx server errors plus 429/503 back-pressure.
RETRYABLE_HTTP_STATUSES: frozenset[int] = frozenset({429, 503})
# Statuses a bot wall uses to refuse a request.
BLOCKING_HTTP_STATUSES: frozenset[int] = frozenset({403, 429, 503})
# Cap how long a server-supplied Retry-After can stall us (seconds).
MAX_RETRY_AFTER_SECONDS: float = 10.0

# Header fingerprints for anti-bot/WAF vendors that front docs hosts.
# Each entry is matched only on a blocking status, except Cloudflare's
# ``cf-mitigated`` which is authoritative regardless of status code.
WAF_HEADER_FINGERPRINTS: tuple[tuple[str, str], ...] = (
    ("x-datadome", "DataDome"),
    ("x-iinfo", "Imperva Incapsula"),
    ("x-amzn-waf-action", "AWS WAF"),
    ("x-sucuri-id", "Sucuri"),
)

# -- User-Agent ----------------------------------------------------------------
try:
    _VERSION = version("llmstxt-mcp")
except PackageNotFoundError:  # pragma: no cover - editable installs without metadata
    _VERSION = "0.0.0"

USER_AGENT = f"llmstxt-mcp/{_VERSION}"

# -- Ecosystem-specific curated lists ------------------------------------------
# Forge hosts where Go module paths follow host/owner/repo and are also valid
# repository URLs. Non-exhaustive — self-hosted instances will still be missed.
GO_FORGE_HOSTS: tuple[str, ...] = (
    "github.com",
    "gitlab.com",
    "bitbucket.org",
    "codeberg.org",
    "git.sr.ht",
    "hg.sr.ht",
    "gitea.com",
    "go.googlesource.com",
)

# Python package names that never have useful third-party docs.
PYTHON_SKIP_PACKAGE_NAMES: frozenset[str] = frozenset({"python", "pip", "setuptools", "wheel"})

# -- MCP server defaults -------------------------------------------------------
DEFAULT_MCP_HOST: str = "127.0.0.1"
DEFAULT_MCP_PORT: int = 8000
