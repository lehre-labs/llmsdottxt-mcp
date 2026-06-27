---
name: architecture
description: Layered import contract.
globs: ["src/llmsdottxt_mcp/**/*.py"]
---
- Layers (high to low): cli → server → tools/resources/prompts → pipeline → scanners/resolvers/platforms/fetcher/index → http → config/errors → models.
- A layer may import only lower layers; siblings stay independent.
- `pipeline` is the only place that wires scanners + resolvers + platforms + fetcher + index together.
- Verify with `uv run lint-imports`; the contract lives in `pyproject.toml`.
