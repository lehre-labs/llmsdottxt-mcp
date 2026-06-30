# Context Routing

Read the narrowest context that explains the code you are changing.

## Order

1. Root `AGENTS.md` for project-wide rules.
2. `CONTEXT-MAP.md` to find the relevant context files.
3. Package-local `AGENTS.md` and `CONTEXT.md` when present.
4. Source files and tests for implementation truth.

## Package Context

| Package | Local files |
|---|---|
| `src/llmsdottxt_mcp/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmsdottxt_mcp/models/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmsdottxt_mcp/config/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmsdottxt_mcp/scanners/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmsdottxt_mcp/resolvers/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmsdottxt_mcp/platforms/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmsdottxt_mcp/tools/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmsdottxt_mcp/resources/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmsdottxt_mcp/prompts/` | `AGENTS.md`, `CONTEXT.md` |

## Focused Notes

- Model / string-alias changes: read the **Typed boundaries** note in [`engineering.md`](./engineering.md), then `models/AGENTS.md`.
- Architecture/import questions: the **Layered architecture** note in [`AGENTS.md`](../../AGENTS.md), enforced by `uv run lint-imports`.

## Rule

Add package-local context only when it prevents repeated mistakes or marks a real ownership boundary.
