"""Gzip-compressed ``llms-full.txt`` cache on the local filesystem."""

from __future__ import annotations

import gzip
from pathlib import Path  # noqa: TC003 — return annotation needs it at runtime-readable scope

from llmsdottxt_mcp.config import settings


def cache_path(package: str, ecosystem: str) -> Path:
    return settings.cache_dir / ecosystem / f"{package}__llms-full.txt.gz"


def cached_full_text(package: str, ecosystem: str) -> str | None:
    path = cache_path(package, ecosystem)
    if not path.is_file():
        return None
    return gzip.decompress(path.read_bytes()).decode()


def cache_full_text(package: str, ecosystem: str, content: str) -> None:
    path = cache_path(package, ecosystem)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(content.encode()))


def total_cache_size() -> int:
    if not settings.cache_dir.is_dir():
        return 0
    return sum(f.stat().st_size for f in settings.cache_dir.rglob("*.gz"))
