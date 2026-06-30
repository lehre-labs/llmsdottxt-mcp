# Resources Context

Read-only `llmstxt://` resource language.

## Language

**Resource**:
A read-only projection of the index exposed as `llmstxt://` URIs -- the package list (`llmstxt://packages`) or a single Index Entry (`llmstxt://package/{ecosystem}/{name}`).
_Avoid_: resource handler, endpoint, URI handler

**Resource Registry**:
The `register_resources(mcp)` entry point that calls per-domain `register(mcp)` to mount every resource URI pattern.
_Avoid_: resource list, resource setup
