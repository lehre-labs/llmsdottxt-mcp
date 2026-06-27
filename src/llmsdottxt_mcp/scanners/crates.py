"""Rust ecosystem scanner: Cargo.toml."""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING, override

import structlog

from llmsdottxt_mcp.models import Dependency, Ecosystem
from llmsdottxt_mcp.scanners.base import BaseScanner

if TYPE_CHECKING:
    from pathlib import Path

logger = structlog.get_logger(__name__)

# Dependency tables in a Cargo manifest. ``workspace.dependencies`` lives under
# ``[workspace]`` and is handled separately.
_DEP_TABLES = ("dependencies", "dev-dependencies", "build-dependencies")


def _make_dep(name: str, spec: str | dict[str, object]) -> Dependency | None:
    """Build a Dependency from a Cargo spec; skip local ``path`` crates."""
    if isinstance(spec, dict):
        if spec.get("path"):  # local crate, not on crates.io
            return None
        version = spec.get("version")
        version_spec = version if isinstance(version, str) else None
    else:
        version_spec = spec or None
    return Dependency(name=name, version_spec=version_spec, ecosystem=Ecosystem.rust)


class CargoTomlScanner(BaseScanner):
    """Scans dependencies from a Cargo.toml manifest."""

    ecosystem = Ecosystem.rust

    @override
    @staticmethod
    def can_handle(project_root: Path) -> bool:
        return (project_root / "Cargo.toml").is_file()

    @override
    def extract_deps(self, project_root: Path) -> list[Dependency]:
        try:
            data = tomllib.loads((project_root / "Cargo.toml").read_text())
        except (OSError, tomllib.TOMLDecodeError) as exc:
            logger.warning("cargo_toml_parse_failed", error=str(exc))
            return []

        tables = [data.get(table, {}) for table in _DEP_TABLES]
        tables.append(data.get("workspace", {}).get("dependencies", {}))

        deps: dict[str, Dependency] = {}
        for table in tables:
            if not isinstance(table, dict):
                continue
            for name, spec in table.items():
                if name not in deps and (dep := _make_dep(name, spec)):
                    deps[name] = dep

        return list(deps.values())
