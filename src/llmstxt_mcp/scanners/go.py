"""Go ecosystem scanner: go.mod."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, override

import structlog

from llmstxt_mcp.models import Dependency, Ecosystem
from llmstxt_mcp.scanners.base import BaseScanner

if TYPE_CHECKING:
    from pathlib import Path

logger = structlog.get_logger(__name__)

# A require line: "<module-path> <version>", optionally trailed by "// indirect".
_REQUIRE_LINE = re.compile(r"^(?P<path>[^\s()]+)\s+(?P<version>v[^\s]+)\s*(?://\s*(?P<note>.*))?$")


class GoModScanner(BaseScanner):
    """Scans direct dependencies from a go.mod file."""

    ecosystem = Ecosystem.go

    @override
    @staticmethod
    def can_handle(project_root: Path) -> bool:
        return (project_root / "go.mod").is_file()

    @override
    def extract_deps(self, project_root: Path) -> list[Dependency]:
        try:
            content = (project_root / "go.mod").read_text()
        except OSError as exc:
            logger.warning("go_mod_parse_failed", error=str(exc))
            return []

        deps: dict[str, Dependency] = {}
        in_block = False
        for raw in content.splitlines():
            line = raw.strip()
            if line.startswith("require ("):
                in_block = True
                continue
            if in_block and line == ")":
                in_block = False
                continue

            if line.startswith("require "):
                line = line.removeprefix("require ").strip()
            elif not in_block:
                continue

            if dep := _parse_require(line):
                deps.setdefault(dep.name, dep)

        return list(deps.values())


def _parse_require(line: str) -> Dependency | None:
    """Parse one require entry; skip ``// indirect`` (transitive) modules."""
    match = _REQUIRE_LINE.match(line)
    if match is None:
        return None
    if (match.group("note") or "").strip() == "indirect":
        return None
    return Dependency(
        name=match.group("path"),
        version_spec=match.group("version"),
        ecosystem=Ecosystem.go,
    )
