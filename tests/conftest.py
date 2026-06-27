"""Shared test fixtures."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from llmsdottxt_mcp import index
from llmsdottxt_mcp.config import settings

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def tmp_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Point the index at a throwaway directory for every test."""
    root = tmp_path / ".llms.txt.d"
    monkeypatch.setattr(settings, "index_root", root)
    settings.ensure_dirs()
    # Reset the global connection to pick up the new index_root.
    index._close_conn_sync()
    return root


@pytest.fixture
def pyproject_dir(tmp_path: Path) -> Path:
    """A directory containing a PEP 621 pyproject.toml."""
    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        "[project]\n"
        'name = "demo"\n'
        'version = "0.1.0"\n'
        'dependencies = ["requests>=2.31", "typer>=0.15", "httpx"]\n'
        "[project.optional-dependencies]\n"
        'dev = ["pytest>=8.0", "ruff"]\n'
    )
    return project


@pytest.fixture
def reqs_dir(tmp_path: Path) -> Path:
    """A directory containing a requirements.txt."""
    project = tmp_path / "reqs"
    project.mkdir()
    (project / "requirements.txt").write_text(
        "requests>=2.31\ntyper\n# a comment\nhttpx==0.28.1\n--index-url https://pypi.org/simple\n"
    )
    return project


@pytest.fixture
def package_json_dir(tmp_path: Path) -> Path:
    """A directory containing a package.json."""
    project = tmp_path / "node"
    project.mkdir()
    (project / "package.json").write_text(
        "{\n"
        '  "name": "demo",\n'
        '  "dependencies": {"react": "^18.2.0", "lodash": "*"},\n'
        '  "devDependencies": {"typescript": "5.4.0"}\n'
        "}\n"
    )
    return project


@pytest.fixture
def cargo_toml_dir(tmp_path: Path) -> Path:
    """A directory containing a Cargo.toml."""
    project = tmp_path / "rust"
    project.mkdir()
    (project / "Cargo.toml").write_text(
        '[package]\nname = "demo"\nversion = "0.1.0"\n\n'
        "[dependencies]\n"
        'serde = "1.0"\n'
        'tokio = { version = "1", features = ["full"] }\n'
        'local = { path = "../local" }\n\n'
        "[dev-dependencies]\n"
        'criterion = "0.5"\n'
    )
    return project


@pytest.fixture
def go_mod_dir(tmp_path: Path) -> Path:
    """A directory containing a go.mod."""
    project = tmp_path / "go"
    project.mkdir()
    (project / "go.mod").write_text(
        "module example.com/demo\n\n"
        "go 1.21\n\n"
        "require github.com/gin-gonic/gin v1.9.1\n\n"
        "require (\n"
        "\tgithub.com/stretchr/testify v1.8.4\n"
        "\tgolang.org/x/sync v0.3.0 // indirect\n"
        ")\n"
    )
    return project


@pytest.fixture
def sample_llms_txt() -> str:
    return (
        "# Requests: HTTP for Humans\n\n"
        "> Requests is an elegant and simple HTTP library for Python.\n\n"
        "## Core Documentation\n\n"
        "- [Quickstart](https://requests.readthedocs.io/en/latest/): Get started\n"
        "- [API Reference](https://requests.readthedocs.io/en/latest/api/): Full API\n\n"
        "## Optional\n\n"
        "- [Contributing](https://requests.readthedocs.io/en/latest/contributing/): How to help\n"
    )
