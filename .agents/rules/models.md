---
name: models
description: Typed model design.
globs: ["src/llmsdottxt_mcp/models/**/*.py"]
---
- Prefer explicit Pydantic models over `dict[str, Any]`.
- `core.py`: domain models (Dependency, DocsInfo, PlatformHint, llms.txt parse tree).
- `index.py`: persisted shapes (IndexEntry, IndexMeta).
- `responses.py`: tool-facing returns (ScanReport, PackageSummary, SearchHit, StatusReport).
- `strings.py`: aliases + enums. Run `uv run ty check` and `uv run basedpyright` after changes.
