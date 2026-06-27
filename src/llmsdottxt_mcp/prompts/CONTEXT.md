# Prompts Context

Reusable documentation-workflow prompt language.

## Language

**Prompt**:
A reusable workflow message (e.g. `find_docs_for_import`) that guides an agent to use the MCP tools in the right order. Prompts reference tools; they never call them directly.
_Avoid_: prompt template, instruction, workflow description, chain

**Prompt Registry**:
The `register_prompts(mcp)` entry point that calls per-domain `register(mcp)` to attach every prompt to the MCP server.
_Avoid_: prompt list, prompt setup
