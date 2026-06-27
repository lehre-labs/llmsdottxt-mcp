---
name: project-workflow
description: Baseline workflow for all repo work.
globs: ["**/*"]
---
- Read `AGENTS.md`, then `CONTEXT-MAP.md` to find the narrowest context.
- Read project config (`pyproject.toml`, `.python-version`, `.env.example`) instead of assuming defaults.
- State assumptions before non-trivial work; surface tradeoffs.
- Keep changes minimal, scoped, and verified.
- Target Python 3.14; the tool is installed with `uvx llmstxt-mcp`.
