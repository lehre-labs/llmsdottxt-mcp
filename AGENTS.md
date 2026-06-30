# AGENTS.md

<critical>
If `@AGENTS.local.md` or `@CLAUDE.local.md` exists, read it for local preferences.
</critical>

This is **llmsdottxt-mcp**. Before doing anything else, read `pyproject.toml` so you know what we're building.

## 1. Build Around ONE IDEA

**Read `@IDEA.md` first. Every change must serve the thesis it states.**

This project exists for one reason. `@IDEA.md` names it, along with the non-goals that bound it. Before any change:

- If the change doesn't serve the IDEA, it doesn't belong here -- say so.
- If it lands in a documented non-goal, stop and flag the conflict.
- If the IDEA itself is unclear or seems wrong for the request, surface that before coding -- don't silently reinterpret it.

## 2. Read the Context

**Before writing any code, understand the user's request and the project's language.**

- Read `@CONTEXT-MAP.md` and `@CONTEXT.md` -- they define what things are called.
- If the term you need is missing, define it there before using it.
- If the user used the wrong term, use the canonical one and note the discrepancy.
- A wrong name in code is worse than a bug.

## 3. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them -- don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 4. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 5. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it -- don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 6. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" -> "Write tests for invalid inputs, then make them pass"
- "Fix the bug" -> "Write a test that reproduces it, then make it pass"
- "Refactor X" -> "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 7. Everything stays Lean

**Say what's needed once. Don't narrate.**

In code:

- Comment *why*, never *what* -- the code already says what.
- No micro-context comments on near-self-explanatory lines.
- No comments that restate the function name, type, or obvious intent.
- No change-log or "I added this" comments -- that's what git is for.

In replies to the human:

- Lead with the answer or result. Cut preamble and recap.
- Don't explain code that speaks for itself.
- Match length to the task: a one-line change gets a one-line reply.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## Project Notes

The checkable, project-specific detail lives in docs so this contract stays lean:

- **Engineering rules** (layered architecture, typed boundaries, MCP contracts, fetch safety, testing, the verify suite): `docs/agents/engineering.md`.
- **Domain language**: one canonical name per concept; `CONTEXT-MAP.md` points at the per-context `CONTEXT.md`.
- **Context routing** (which `AGENTS.md`/`CONTEXT.md` to read per area): `docs/agents/context-routing.md`.

## Agent skills

Invoke applicable skills under `.agents/skills` don't guess the workflow.

### Issue tracker
Issues and PRDs live as GitHub issues, driven via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels
Five canonical roles: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs
Multi-context: `CONTEXT-MAP.md` at the root points at one `CONTEXT.md` per context; ADRs live in `docs/adr/`. See `docs/agents/domain.md`.

## Footnotes

**Prompts are technical debt.** Prompts (AGENTS.md, CLAUDE.md, skills, system prompts) are a worse form of technical debt than code. They're model-specific -- a prompt tuned for one model can silently degrade or become harmful after a model upgrade. Unlike buggy code, prompt decay doesn't throw errors; you just get subtly worse results. Avoid behavior steering ("think step by step", "you are a skilled engineer") and keep files limited to concrete, project-specific facts. Write prompts yourself. Delete them whenever you can.

**Principles ≠ Rules.** Principles 1-7 are behavioral guidelines and judgment calls. Rules -- enforceable, automated, or explicitly checkable constraints -- live in `docs/agents/engineering.md` and are enforced by the tooling configured in `pyproject.toml` (`ruff`, `ty`, `basedpyright`, `import-linter`, `bandit`). Principles guide how to think; rules define what must or must not happen.

<critical>
Alongside this `AGENTS.md`, keep a sibling `CLAUDE.md` whose entire content is the single line `@AGENTS.md`. `AGENTS.md` is canonical; `CLAUDE.md` only includes it, so a harness keyed on either name loads the same contract. Edit `AGENTS.md` only -- never let the two drift.
</critical>
