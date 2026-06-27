"""npm ecosystem scanner: package.json."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, override

import structlog

from llmstxt_mcp.models import Dependency, Ecosystem
from llmstxt_mcp.scanners.base import BaseScanner

if TYPE_CHECKING:
    from pathlib import Path

logger = structlog.get_logger(__name__)

# Dependency tables we treat as direct deps worth documenting.
_DEP_FIELDS = ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")


class PackageJsonScanner(BaseScanner):
    """Scans dependencies from a package.json manifest."""

    ecosystem = Ecosystem.node

    @override
    @staticmethod
    def can_handle(project_root: Path) -> bool:
        return (project_root / "package.json").is_file()

    @override
    def extract_deps(self, project_root: Path) -> list[Dependency]:
        try:
            data = json.loads((project_root / "package.json").read_text())
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("package_json_parse_failed", error=str(exc))
            return []

        deps: dict[str, Dependency] = {}
        for field in _DEP_FIELDS:
            table = data.get(field)
            if not isinstance(table, dict):
                continue
            for name, spec in table.items():
                if name and name not in deps:
                    deps[name] = Dependency(
                        name=name,
                        version_spec=spec if isinstance(spec, str) and spec != "*" else None,
                        ecosystem=Ecosystem.node,
                    )

        return list(deps.values())
