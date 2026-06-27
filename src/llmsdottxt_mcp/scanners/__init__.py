"""Scanner registry: registration and ecosystem detection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmsdottxt_mcp.scanners.base import BaseScanner
from llmsdottxt_mcp.scanners.crates import CargoTomlScanner
from llmsdottxt_mcp.scanners.go import GoModScanner
from llmsdottxt_mcp.scanners.npm import PackageJsonScanner
from llmsdottxt_mcp.scanners.python import PyprojectTomlScanner, RequirementsTxtScanner

if TYPE_CHECKING:
    from pathlib import Path

SCANNER_REGISTRY: list[type[BaseScanner]] = [
    PyprojectTomlScanner,
    RequirementsTxtScanner,
    PackageJsonScanner,
    CargoTomlScanner,
    GoModScanner,
]


def detect_ecosystem(project_root: Path) -> BaseScanner | None:
    """Return the first registered scanner that can handle the project."""
    for scanner_cls in SCANNER_REGISTRY:
        if scanner_cls.can_handle(project_root):
            return scanner_cls()
    return None


__all__ = ["SCANNER_REGISTRY", "BaseScanner", "detect_ecosystem"]
