"""CLI command tests (Typer CliRunner).

These assert two things per command: the documented output shape, and that the
global index connection is closed afterwards. The latter guards the CLI-hang
regression — aiosqlite's connection thread is non-daemon, so an un-closed
connection would prevent the process from exiting.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from typer.testing import CliRunner

from llmstxt_mcp import index, pipeline
from llmstxt_mcp.cli import app
from llmstxt_mcp.models import Ecosystem, IndexEntry, ParsedLlmsTxt, Platform, ScanReport

if TYPE_CHECKING:
    import pytest
    from pytest_httpx import HTTPXMock

runner = CliRunner()


def _entry(package: str = "requests") -> IndexEntry:
    return IndexEntry(
        package=package,
        ecosystem=Ecosystem.python,
        latest_version="2.32.3",
        docs_base_url="https://requests.readthedocs.io",
        platform=Platform.readthedocs,
        has_full_text=True,
        full_text_size=2 * 1024 * 1024,
        llms_txt=ParsedLlmsTxt(title="Requests"),
        indexed_at="2026-06-27T00:00:00Z",
    )


async def _seed(*packages: str) -> None:
    for package in packages:
        await index.add(_entry(package))
    await index.close()


def test_status_empty_exits_clean() -> None:
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Packages:   0 indexed" in result.stdout
    assert index._conn is None


def test_status_lists_packages_as_tsv() -> None:
    asyncio.run(_seed("requests"))
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    rows = [line for line in result.stdout.splitlines() if "\t" in line]
    assert rows, "expected at least one tab-separated package row"
    fields = rows[0].split("\t")
    assert fields[0] == "requests"
    assert fields[1] == "python"
    assert fields[2] == "2.32.3"
    assert index._conn is None


def test_scan_reports_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_scan(root: object, refresh: bool = False) -> ScanReport:
        return ScanReport(
            project_root=str(root), scanned=3, indexed=2, missing=1, ecosystems=[Ecosystem.python]
        )

    monkeypatch.setattr(pipeline, "scan_project", fake_scan)
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 0
    assert "Scanned" in result.stdout
    assert "Indexed" in result.stdout


def test_scan_no_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_scan(root: object, refresh: bool = False) -> ScanReport:
        return ScanReport(project_root=str(root), scanned=0, indexed=0, missing=0)

    monkeypatch.setattr(pipeline, "scan_project", fake_scan)
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 0
    assert "No dependencies" in result.stdout


def test_scan_reports_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_scan(root: object, refresh: bool = False) -> ScanReport:
        return ScanReport(project_root=str(root), scanned=5, indexed=2, missing=1, blocked=2)

    monkeypatch.setattr(pipeline, "scan_project", fake_scan)
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 0
    assert "blocked" in result.stdout


def test_clear_force() -> None:
    asyncio.run(_seed("requests"))
    result = runner.invoke(app, ["clear", "--force"])
    assert result.exit_code == 0
    assert "cleared" in result.stdout.lower()
    assert index._conn is None


def test_clear_aborted() -> None:
    result = runner.invoke(app, ["clear"], input="n\n")
    assert result.exit_code == 0
    assert "Aborted" in result.stdout


def test_doctor_emits_tsv_and_exits_clean(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://pypi.org/pypi/pip/json", json={"info": {}})
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "pypi reachable\tok" in result.stdout
    assert index._conn is None
