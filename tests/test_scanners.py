"""Scanner tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmsdottxt_mcp.models import Ecosystem
from llmsdottxt_mcp.scanners import detect_ecosystem
from llmsdottxt_mcp.scanners.crates import CargoTomlScanner
from llmsdottxt_mcp.scanners.go import GoModScanner
from llmsdottxt_mcp.scanners.npm import PackageJsonScanner
from llmsdottxt_mcp.scanners.python import PyprojectTomlScanner, RequirementsTxtScanner

if TYPE_CHECKING:
    from pathlib import Path


def test_detect_pyproject(pyproject_dir: Path) -> None:
    scanner = detect_ecosystem(pyproject_dir)
    assert isinstance(scanner, PyprojectTomlScanner)
    assert scanner.ecosystem == Ecosystem.python


def test_detect_requirements(reqs_dir: Path) -> None:
    assert isinstance(detect_ecosystem(reqs_dir), RequirementsTxtScanner)


def test_detect_none(tmp_path: Path) -> None:
    assert detect_ecosystem(tmp_path) is None


def test_pyproject_extracts_deps(pyproject_dir: Path) -> None:
    deps = PyprojectTomlScanner().extract_deps(pyproject_dir)
    names = {d.name for d in deps}
    assert {"requests", "typer", "httpx", "pytest", "ruff"} <= names
    assert all(d.ecosystem == Ecosystem.python for d in deps)


def test_pyproject_strips_version_and_extras(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        '[project]\nname="x"\nversion="0"\ndependencies=["requests[socks]>=2.0", "uvicorn"]\n'
    )
    deps = {d.name: d for d in PyprojectTomlScanner().extract_deps(project)}
    assert deps["requests"].version_spec == ">=2.0"
    assert deps["uvicorn"].version_spec is None


def test_requirements_skips_comments_and_flags(reqs_dir: Path) -> None:
    names = {d.name for d in RequirementsTxtScanner().extract_deps(reqs_dir)}
    assert names == {"requests", "typer", "httpx"}


def test_detect_package_json(package_json_dir: Path) -> None:
    scanner = detect_ecosystem(package_json_dir)
    assert isinstance(scanner, PackageJsonScanner)
    assert scanner.ecosystem == Ecosystem.node


def test_package_json_extracts_deps(package_json_dir: Path) -> None:
    deps = {d.name: d for d in PackageJsonScanner().extract_deps(package_json_dir)}
    assert set(deps) == {"react", "lodash", "typescript"}
    assert deps["react"].version_spec == "^18.2.0"
    assert deps["lodash"].version_spec is None  # "*" means any
    assert all(d.ecosystem == Ecosystem.node for d in deps.values())


def test_detect_cargo_toml(cargo_toml_dir: Path) -> None:
    assert isinstance(detect_ecosystem(cargo_toml_dir), CargoTomlScanner)


def test_cargo_toml_extracts_deps(cargo_toml_dir: Path) -> None:
    deps = {d.name: d for d in CargoTomlScanner().extract_deps(cargo_toml_dir)}
    # "local" is a path crate, not on crates.io -> skipped.
    assert set(deps) == {"serde", "tokio", "criterion"}
    assert deps["serde"].version_spec == "1.0"
    assert deps["tokio"].version_spec == "1"
    assert all(d.ecosystem == Ecosystem.rust for d in deps.values())


def test_detect_go_mod(go_mod_dir: Path) -> None:
    assert isinstance(detect_ecosystem(go_mod_dir), GoModScanner)


def test_go_mod_extracts_direct_deps(go_mod_dir: Path) -> None:
    deps = {d.name: d for d in GoModScanner().extract_deps(go_mod_dir)}
    # golang.org/x/sync is "// indirect" -> skipped.
    assert set(deps) == {"github.com/gin-gonic/gin", "github.com/stretchr/testify"}
    assert deps["github.com/gin-gonic/gin"].version_spec == "v1.9.1"
    assert all(d.ecosystem == Ecosystem.go for d in deps.values())


def test_pyproject_poetry_deps(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        "[tool.poetry.dependencies]\n"
        'python = "^3.10"\n'
        'uvicorn = "*"\n'
        "[tool.poetry.dev-dependencies]\n"
        'black = "^24.0"\n'
    )
    deps = {d.name: d for d in PyprojectTomlScanner().extract_deps(project)}
    assert set(deps) == {"uvicorn", "black"}


def test_pyproject_skips_core_names(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        '[project]\nname="x"\nversion="0"\ndependencies=["python", "pip", "setuptools", "wheel"]\n'
    )
    assert PyprojectTomlScanner().extract_deps(project) == []


def test_pyproject_parse_error_returns_empty(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "pyproject.toml").write_text("not valid toml {{{")
    assert PyprojectTomlScanner().extract_deps(project) == []


def test_requirements_missing_file(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    # requirements.txt doesn't exist, but can_handle already checked so
    # extract_deps hits OSError when reading the missing file.
    assert RequirementsTxtScanner().extract_deps(project) == []


def test_requirements_with_inline_comments(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "requirements.txt").write_text(
        "requests>=2.0  # the http client\ntyper  # CLI framework\n"
    )
    deps = {d.name: d for d in RequirementsTxtScanner().extract_deps(project)}
    assert set(deps) == {"requests", "typer"}


def test_package_json_parse_error_returns_empty(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "package.json").write_text("not valid json")
    assert PackageJsonScanner().extract_deps(project) == []


def test_package_json_peer_deps(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "package.json").write_text(
        '{"peerDependencies": {"react": ">=18"}, "optionalDependencies": {"fsevents": "2.3"}}'
    )
    deps = {d.name: d for d in PackageJsonScanner().extract_deps(project)}
    assert set(deps) == {"react", "fsevents"}


def test_cargo_toml_parse_error_returns_empty(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "Cargo.toml").write_text("not toml {{{")
    assert CargoTomlScanner().extract_deps(project) == []


def test_cargo_toml_workspace_deps(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "Cargo.toml").write_text(
        '[workspace.dependencies]\nserde = "1.0"\ntokio = { version = "1", features = ["full"] }\n'
    )
    deps = {d.name: d for d in CargoTomlScanner().extract_deps(project)}
    assert set(deps) == {"serde", "tokio"}


def test_go_mod_parse_error_returns_empty(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "go.mod").write_text("not a go.mod")
    assert GoModScanner().extract_deps(project) == []


def test_go_mod_single_line_require(tmp_path: Path) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "go.mod").write_text(
        "module example\n\ngo 1.21\n\nrequire github.com/foo/bar v1.2.3\n"
    )
    deps = {d.name: d for d in GoModScanner().extract_deps(project)}
    assert set(deps) == {"github.com/foo/bar"}
