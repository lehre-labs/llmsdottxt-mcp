"""Orchestration: scan a project and resolve documentation on demand.

This is the single place that wires scanners -> resolver -> platforms -> fetcher
-> index together, shared by both the CLI and the MCP tools.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog

from llmsdottxt_mcp import index
from llmsdottxt_mcp.config import settings
from llmsdottxt_mcp.errors import BlockedByChallengeError, FetchError, PackageNotIndexedError
from llmsdottxt_mcp.fetcher import fetch_full_text, fetch_llms_txt
from llmsdottxt_mcp.http import build_client
from llmsdottxt_mcp.models import DocsInfo, Ecosystem, IndexEntry, IndexMeta, ScanReport
from llmsdottxt_mcp.platforms import detect_platform
from llmsdottxt_mcp.resolvers import resolve
from llmsdottxt_mcp.scanners import detect_ecosystem

if TYPE_CHECKING:
    from pathlib import Path

    import httpx

    from llmsdottxt_mcp.models import Dependency

logger = structlog.get_logger(__name__)


async def scan_project(root: Path, *, refresh: bool = False) -> ScanReport:
    """Scan a project's dependencies and index discoverable llms.txt docs."""
    settings.ensure_dirs()

    scanner = detect_ecosystem(root)
    if scanner is None:
        return ScanReport(project_root=str(root), scanned=0, indexed=0, missing=0)

    deps = scanner.extract_deps(root)
    if not deps:
        return ScanReport(
            project_root=str(root), scanned=0, indexed=0, missing=0, ecosystems=[scanner.ecosystem]
        )

    semaphore = asyncio.Semaphore(settings.max_concurrent_fetches)
    counters = {"indexed": 0, "missing": 0, "blocked": 0}

    async with build_client() as client:
        await asyncio.gather(
            *(_index_one(dep, client, semaphore, counters, refresh=refresh) for dep in deps)
        )

    ecosystems = sorted({dep.ecosystem for dep in deps})
    await _write_meta(root, deps, ecosystems)

    return ScanReport(
        project_root=str(root),
        scanned=len(deps),
        indexed=counters["indexed"],
        missing=counters["missing"],
        blocked=counters["blocked"],
        ecosystems=ecosystems,
    )


async def _index_one(
    dep: Dependency,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    counters: dict[str, int],
    *,
    refresh: bool,
) -> None:
    async with semaphore:
        if not refresh and await index.get(dep.name, dep.ecosystem):
            counters["indexed"] += 1
            return

        try:
            info = await resolve(dep.name, dep.ecosystem, client)
            if info is None or not info.docs_base_url:
                counters["missing"] += 1
                return

            platform = await detect_platform(info.docs_base_url, client)
            result = await fetch_llms_txt(info, platform, client)
            if result is None:
                counters["missing"] += 1
                return

            full_text = await fetch_full_text(info, platform, client)
        except BlockedByChallengeError as exc:
            logger.info("docs_host_blocked", package=dep.name, url=exc.url, vendor=exc.vendor)
            counters["blocked"] += 1
            return

        if full_text:
            index.cache_full_text(dep.name, dep.ecosystem.value, full_text)

        await index.add(
            IndexEntry(
                package=dep.name,
                ecosystem=dep.ecosystem,
                version_spec=dep.version_spec,
                latest_version=info.latest_version,
                docs_base_url=info.docs_base_url,
                docs_url_source=info.docs_url_source,
                repository_url=info.repository_url,
                platform=platform.platform,
                has_full_text=full_text is not None,
                full_text_size=len(full_text) if full_text else 0,
                llms_txt=result.parsed,
                indexed_at=datetime.now(UTC).isoformat(),
            )
        )
        counters["indexed"] += 1


async def _write_meta(root: Path, deps: list[Dependency], ecosystems: list[Ecosystem]) -> None:
    await index.write_meta(
        IndexMeta(
            last_scan=datetime.now(UTC).isoformat(),
            project_root=str(root),
            ecosystems=[eco.value for eco in ecosystems],
            package_count=len(deps),
            packages={
                eco.value: [d.name for d in deps if d.ecosystem == eco] for eco in ecosystems
            },
        )
    )


async def get_full_text(package: str, ecosystem: str | None = None) -> str:
    """Return cached full docs for a package, fetching on demand if needed."""
    entry = await index.find(package, ecosystem)
    if entry is None:
        raise PackageNotIndexedError(package)

    eco = entry.ecosystem
    cached = index.cached_full_text(package, eco.value)
    if cached:
        return cached

    if entry.docs_base_url:
        async with build_client(settings.full_text_timeout) as client:
            platform = await detect_platform(entry.docs_base_url, client)
            docs_info = DocsInfo(package=package, ecosystem=eco, docs_base_url=entry.docs_base_url)
            content = await fetch_full_text(docs_info, platform, client)
            if content:
                index.cache_full_text(package, eco.value, content)
                entry.has_full_text = True
                entry.full_text_size = len(content)
                await index.add(entry)
                return content

    msg = f"No full documentation available for '{package}' (no llms-full.txt found)."
    raise FetchError(msg)
