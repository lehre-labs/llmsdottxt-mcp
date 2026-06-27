---
name: tests
description: Test strategy and coverage.
globs: ["tests/**/*.py"]
---
- Mirror `src/` structure; reproduce bugs before fixing them.
- Mock HTTP with `pytest-httpx`; never hit the live network in unit tests (use the `live` marker for opt-in).
- The autouse `tmp_index` fixture points the index at a temp dir — rely on it.
- Run `uv run pytest -n auto`; keep coverage above the `fail_under` gate.
