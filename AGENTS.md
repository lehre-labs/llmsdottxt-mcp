# AGENTS.md

<critical>
This file encodes the project's shared coding discipline. For local-only overrides — tool aliases, editor preferences, personal shortcuts — create an `AGENTS.local.md` next to this file. It is git-ignored and sourced after this file, so it can shadow or extend any heading without branching the shared rules.
</critical>

We're building **llmsdottxt-mcp** — a local-first MCP server that scans a project's dependencies, discovers their `llms.txt` documentation endpoints, fetches and indexes the content, and exposes it to AI coding agents through **FastMCP**. Installed with `uvx llmsdottxt-mcp`.

## Domain Language

Every concept has one name. Synonyms are banned. See [`CONTEXT-MAP.md`](./CONTEXT-MAP.md) to find the relevant context file. If a term is missing, define it in the narrowest applicable `CONTEXT.md`.

## Layered Architecture

Imports flow downward only (enforced by `import-linter`, run `uv run lint-imports`):

```
cli → server → tools / resources / prompts → pipeline
    → scanners / resolvers / platforms / fetcher / index → http → config / errors → models
```

- `pipeline` is the single orchestrator that wires the discovery layer together.
- `resolvers/` and `platforms/` are registry packages — add an ecosystem or platform by dropping one module in and registering it. `scanners/` follows the same pattern.

## Typed Boundaries

- Put constrained string aliases and finite enums in `models/strings.py`.
- Use `StrEnum` for finite protocol values (`Ecosystem`, `Platform`, `DocsUrlSource`) and a `Literal` (`LogLevel`) for log levels.
- Model persisted and tool-facing data with Pydantic — avoid `dict[str, Any]`.
- Validate user-supplied tool inputs strictly; keep fetched third-party docs tolerant.
- Pydantic and FastMCP resolve annotations at runtime, so field and tool-return types must be importable at runtime, not hidden under `TYPE_CHECKING`.

## Code Principles

### 1. Think Before Coding
Don’t assume. Don’t hide confusion. Surface tradeoffs.
Before implementing:
* State your assumptions explicitly. If uncertain, ask.
* If multiple interpretations exist, present them — don’t pick silently.
* If a simpler approach exists, say so. Push back when warranted.
* If something is unclear, stop. Name what’s confusing. Ask.

### 2. Simplicity First
Minimum code that solves the problem. Nothing speculative.
* No features beyond what was asked.
* No abstractions for single-use code.
* No "flexibility" or "configurability" that wasn’t requested.
* No error handling for impossible scenarios.
* If you write 200 lines and it could be 50, rewrite it.
Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes
Touch only what you must. Clean up only your own mess.
* Don’t "improve" adjacent code, comments, or formatting.
* Don’t refactor things that aren’t broken.
* Match existing style, even if you’d do it differently.
* If you notice unrelated dead code, mention it — don’t delete it.
When your changes create orphans:
* Remove imports/variables/functions that YOUR changes made unused.
* Don’t remove pre-existing dead code unless asked.
The test: every changed line should trace directly to the user’s request.

### 4. Goal-Driven Execution
Define success criteria. Loop until verified.
Transform tasks into verifiable goals:
* "Add validation" → "Write tests for invalid inputs, then make them pass"
* "Fix the bug" → "Write a test that reproduces it, then make it pass"
* "Refactor X" → "Ensure tests pass before and after"
For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```
Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

### 5. Domain Integrity
One canonical name per concept.
* Every concept has one name; synonyms are banned.
* See `CONTEXT-MAP.md` to find the relevant context file.
* If a term is missing, define it in the narrowest applicable `CONTEXT.md`.
* Never reuse a term that’s already claimed in a parent context.
* These principles are working when diffs are minimal, rewrites are rare, and clarifying questions come before implementation rather than after mistakes.

## Observability & Safety

- stdout is the MCP stdio channel — **never `print()`** in library code. Logs are JSON on stderr via `structlog` (`config/logging.py`).
- Route all HTTP through `llmsdottxt_mcp.http` for retry + rate-limiting.
- Treat fetched llms.txt content as untrusted; cap size; never commit the `~/.llms.txt.d/` cache.

## Project Config

Read these instead of relying on hardcoded conventions:

- `pyproject.toml` — dependencies, tool config (ruff, ty, basedpyright, pytest, import-linter).
- `.python-version` — Python runtime (3.14).
- `.env.example` — optional `LLMSTXT_*` settings.

## Testing

`pytest` + `pytest-cov` (+ `pytest-xdist` for `-n auto`), `pytest-httpx` for mocking docs hosts, `hypothesis` for pure helpers. Tests mirror `src/`. Write a test for every new function or bug fix. Use the `live` marker for opt-in network tests.

## Verify

```sh
uv run ruff format --check
uv run ruff check
uv run ty check
uv run basedpyright
uv run lint-imports
uv run deptry .
uv run bandit -q -c pyproject.toml -r src
uv run pytest -n auto
```
