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
| `src/llmstxt_mcp/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmstxt_mcp/models/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmstxt_mcp/config/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmstxt_mcp/scanners/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmstxt_mcp/resolvers/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmstxt_mcp/platforms/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmstxt_mcp/tools/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmstxt_mcp/resources/` | `AGENTS.md`, `CONTEXT.md` |
| `src/llmstxt_mcp/prompts/` | `AGENTS.md`, `CONTEXT.md` |

## Focused Notes

- Model / string-alias changes: read [`typed-python.md`](./typed-python.md), then `models/AGENTS.md`.
- Architecture/import questions: `.agents/rules/architecture.md`.

## Rule

Add package-local context only when it prevents repeated mistakes or marks a real ownership boundary.
