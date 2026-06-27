---
name: docs-context
description: Documentation routing.
globs: ["docs/**/*", "**/AGENTS.md", "**/CONTEXT.md"]
---
- Agent-facing docs live in `docs/agents/`; human guides in `docs/human/`.
- Use `docs/agents/source-map.md` when a dependency's behavior may have changed.
- Add package-local `AGENTS.md`/`CONTEXT.md` only when it prevents repeated mistakes.
