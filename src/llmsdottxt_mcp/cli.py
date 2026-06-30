"""Typer CLI: scan, serve, status, clear."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx
from rich.console import Console
import typer

from llmsdottxt_mcp import index, pipeline
from llmsdottxt_mcp.config import DEFAULT_MCP_HOST, DEFAULT_MCP_PORT, configure_logging, settings
from llmsdottxt_mcp.models import IndexMeta, PackageSummary, Transport

if TYPE_CHECKING:
    from collections.abc import Coroutine

app = typer.Typer(
    help="Auto-discover llms.txt from your deps. Docs your agent can read. Zero setup.",
    no_args_is_help=True,
)
console = Console()


def _run[T](coro: Coroutine[Any, Any, T]) -> T:
    """Run an async index operation, then close the global connection.

    aiosqlite's connection runs on a non-daemon thread, so a short-lived CLI
    process would hang on exit if the connection were left open. Closing it
    after each command lets the interpreter terminate cleanly.
    """

    async def _runner() -> T:
        try:
            return await coro
        finally:
            await index.close()

    return asyncio.run(_runner())


@app.command()
def scan(
    root: str | None = typer.Option(None, help="Project root (default: cwd)."),
    refresh: bool = typer.Option(False, help="Re-fetch already-indexed packages."),
) -> None:
    """Scan project dependencies, discover llms.txt, build the local index."""
    configure_logging(settings.log_level)
    project_root = Path(root).resolve() if root else Path.cwd()
    report = _run(pipeline.scan_project(project_root, refresh=refresh))

    if report.scanned == 0:
        console.print("[yellow]No dependencies found[/] (no supported manifest or empty deps).")
        raise typer.Exit(0)

    line = (
        f"Scanned [bold]{report.scanned}[/] dependencies. "
        f"Indexed [green]{report.indexed}[/] with llms.txt. "
    )
    if report.blocked:
        line += f"[yellow]{report.blocked} blocked[/] (bot challenge). "
    line += f"[dim]{report.missing} missing.[/]"
    console.print(line)


@app.command()
def serve(
    transport: Transport = Transport.stdio,
    host: str = DEFAULT_MCP_HOST,
    port: int = DEFAULT_MCP_PORT,
) -> None:
    """Start the MCP server."""
    configure_logging(settings.log_level)
    settings.ensure_dirs()
    from llmsdottxt_mcp.server import serve as _serve

    _serve(transport=transport, host=host, port=port)


@app.command()
def status() -> None:
    """Show index statistics, then one tab-separated line per indexed package.

    Package rows are emitted as ``name<TAB>ecosystem<TAB>version<TAB>platform<TAB>full_text``
    so the output stays grep/fzf-friendly for computer use (no box-drawing tables).
    """
    meta, summaries = _run(_load_status())

    console.print(f"Ecosystems: {', '.join(meta.ecosystems) or 'none'}")
    console.print(f"Packages:   {len(summaries)} indexed")
    console.print(f"Cache:      {index.total_cache_size() / 1024 / 1024:.1f} MB")
    console.print(f"Last scan:  {meta.last_scan or 'never'}")

    # Plain print (not Rich) so tabs stay literal and lines are never wrapped --
    # keeps the rows consumable by fzf/grep/awk under computer use.
    for s in summaries:
        size = f"{s.full_text_size / 1024 / 1024:.1f}MB" if s.has_full_text else "-"
        print(
            "\t".join(
                (
                    s.package,
                    s.ecosystem.value,
                    s.version or "-",
                    s.platform.value if s.platform else "-",
                    size,
                )
            )
        )


async def _load_status() -> tuple[IndexMeta, list[PackageSummary]]:
    meta = await index.read_meta()
    summaries = await index.summaries()
    return meta, summaries


@app.command()
def doctor() -> None:
    """Diagnose the environment: paths, write access, and registry connectivity."""
    configure_logging(settings.log_level)
    ok = _run(_run_doctor())
    raise typer.Exit(0 if ok else 1)


async def _run_doctor() -> bool:
    from llmsdottxt_mcp.http import build_client, get

    checks: list[tuple[str, bool, str]] = []

    checks.append(("index root", True, str(settings.index_root)))

    try:
        settings.ensure_dirs()
        probe = settings.index_root / ".write-probe"
        probe.write_text("ok")
        probe.unlink()
        checks.append(("index writable", True, str(settings.index_root)))
    except OSError as exc:
        checks.append(("index writable", False, str(exc)))

    try:
        async with build_client(timeout=settings.http_timeout) as client:
            response = await get(client, "https://pypi.org/pypi/pip/json")
        reachable = response.status_code == 200
        checks.append(("pypi reachable", reachable, f"HTTP {response.status_code}"))
    except (OSError, httpx.HTTPError) as exc:
        checks.append(("pypi reachable", False, str(exc)))

    packages = await index.list_all()
    checks.append(("packages indexed", True, str(len(packages))))

    # One tab-separated line per check (name<TAB>ok|fail<TAB>detail) -- grep/fzf-friendly.
    for name, passed, detail in checks:
        print("\t".join((name, "ok" if passed else "fail", detail)))

    return all(passed for _, passed, _ in checks)


@app.command()
def clear(force: bool = typer.Option(False, help="Skip the confirmation prompt.")) -> None:
    """Remove all indexed data."""
    if not force and not typer.confirm("Remove all indexed documentation?"):
        console.print("Aborted.")
        raise typer.Exit(0)
    _run(index.clear_all())
    console.print("All index and cache data cleared.")


def main() -> None:
    """Entry point for the console script."""
    app()


if __name__ == "__main__":
    main()
