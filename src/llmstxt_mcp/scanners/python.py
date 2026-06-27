"""Python ecosystem scanners: pyproject.toml + requirements.txt."""

from __future__ import annotations

import re
import tomllib
from typing import TYPE_CHECKING, override

import structlog

from llmstxt_mcp.config import PYTHON_SKIP_PACKAGE_NAMES
from llmstxt_mcp.models import Dependency, Ecosystem
from llmstxt_mcp.scanners.base import BaseScanner

if TYPE_CHECKING:
    from pathlib import Path

logger = structlog.get_logger(__name__)


def _clean_dep_name(raw: str) -> str:
    """Strip extras and version operators from a dependency spec."""
    raw = re.sub(r"\[.*\]", "", raw)  # drop extras: requests[socks] -> requests
    return re.split(r"[<>=!~;\s]", raw)[0].strip()


def _extract_version_spec(raw: str) -> str | None:
    """Extract the version specifier if present."""
    match = re.search(r"([<>=!~]+[^;]+)", raw)
    return match.group(1).strip() if match else None


def _make_dep(raw: str) -> Dependency | None:
    """Build a Dependency from a raw spec, or None if it should be skipped."""
    name = _clean_dep_name(raw)
    if not name or name.lower() in PYTHON_SKIP_PACKAGE_NAMES:
        return None
    return Dependency(
        name=name,
        version_spec=_extract_version_spec(raw),
        ecosystem=Ecosystem.python,
    )


class PyprojectTomlScanner(BaseScanner):
    """Scans PEP 621 and Poetry dependencies from pyproject.toml."""

    ecosystem = Ecosystem.python

    @override
    @staticmethod
    def can_handle(project_root: Path) -> bool:
        return (project_root / "pyproject.toml").is_file()

    @override
    def extract_deps(self, project_root: Path) -> list[Dependency]:
        try:
            data = tomllib.loads((project_root / "pyproject.toml").read_text())
        except (OSError, tomllib.TOMLDecodeError) as exc:
            logger.warning("pyproject_parse_failed", error=str(exc))
            return []

        deps: list[Dependency] = []
        project = data.get("project", {})

        for raw in project.get("dependencies", []):
            if dep := _make_dep(raw):
                deps.append(dep)

        for extra in project.get("optional-dependencies", {}).values():
            for raw in extra:
                if dep := _make_dep(raw):
                    deps.append(dep)

        poetry = data.get("tool", {}).get("poetry", {})
        for group in ("dependencies", "dev-dependencies"):
            for name, spec in poetry.get(group, {}).items():
                if isinstance(spec, str) and name.lower() not in PYTHON_SKIP_PACKAGE_NAMES:
                    deps.append(
                        Dependency(
                            name=name,
                            version_spec=spec if spec != "*" else None,
                            ecosystem=Ecosystem.python,
                        )
                    )

        return deps


class RequirementsTxtScanner(BaseScanner):
    """Scans dependencies from a requirements.txt file."""

    ecosystem = Ecosystem.python

    @override
    @staticmethod
    def can_handle(project_root: Path) -> bool:
        return (project_root / "requirements.txt").is_file()

    @override
    def extract_deps(self, project_root: Path) -> list[Dependency]:
        try:
            content = (project_root / "requirements.txt").read_text()
        except OSError as exc:
            logger.warning("requirements_parse_failed", error=str(exc))
            return []

        deps: list[Dependency] = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "-")):
                continue
            stripped = re.split(r"\s#", stripped)[0].strip()
            if dep := _make_dep(stripped):
                deps.append(dep)

        return deps
