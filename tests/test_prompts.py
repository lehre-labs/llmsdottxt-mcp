"""Prompt tests."""

from __future__ import annotations

from llmsdottxt_mcp.prompts.docs import find_docs_for_import


def test_find_docs_for_import_uses_package_root() -> None:
    text = find_docs_for_import("httpx.AsyncClient")
    # Strips the symbol down to the importable package for search/browse.
    assert "search" in text
    assert "index_deps" in text
    assert "browse(package='httpx')" in text
    assert "httpx.AsyncClient" in text


def test_find_docs_for_import_bare_symbol() -> None:
    text = find_docs_for_import("requests")
    assert "browse(package='requests')" in text
