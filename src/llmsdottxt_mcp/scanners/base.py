"""Base scanner interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from llmsdottxt_mcp.models import Dependency, Ecosystem


class BaseScanner(ABC):
    """Extracts direct dependencies from a project's manifest."""

    ecosystem: Ecosystem

    @staticmethod
    @abstractmethod
    def can_handle(project_root: Path) -> bool:
        """Can this scanner handle the project at this path?"""

    @abstractmethod
    def extract_deps(self, project_root: Path) -> list[Dependency]:
        """Extract direct dependencies from the manifest."""
