# llmsdottxt-mcp

**`llms.txt` will be how agents read docs -- so serve it to them natively, from the deps a project already has.**

Docs were written for humans skimming a browser. Agents don't skim; they retrieve. `llms.txt` is the emerging convention for agent-readable docs, and a project already declares exactly which libraries it depends on -- in `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`. llmsdottxt-mcp closes the loop between those two facts: it reads the real dependency manifests, discovers each package's `llms.txt` endpoint, indexes it locally, and serves it over the protocol agents already speak (MCP). No central catalog to be listed in, no per-repo URL to paste -- the docs an agent needs are the docs for the code it is already editing.

## Problem

An agent editing a codebase has the dependency list right there, but no first-party path to those libraries' docs. So it does one of three lossy things: answers from stale training data (hallucinated APIs, deprecated patterns), scrapes human HTML and burns context on nav chrome, or asks the user to wire up a docs tool per library. Meanwhile `llms.txt` -- the format built for exactly this -- already exists on the docs hosts, unused at the point of work. The gap isn't "docs for LLMs"; it's that nothing connects *this project's actual dependencies* to *their agent-readable docs* without manual setup or a hosted middleman.

## Approach

Discovery is driven by the project's own manifests, not a global index. Pair a manifest scanner with a registry resolver per ecosystem (PyPI, npm, crates.io, Go proxy) to turn a dependency into a docs URL, detect the docs platform (Mintlify, Read the Docs, Docusaurus, …), fetch `llms.txt`/`llms-full.txt`, and persist a searchable index under `~/.llms.txt.d/`. Everything is local-first and convention-based: the index is yours, the fetch path is yours, and a docs host that pushes back with a real `429`/`503` is retried while an unsolvable bot challenge is reported as *blocked* rather than silently miscounted as "no docs".

## Non-Goals

- **Not a hosted documentation service.** No central catalog, no account, no API key. The index lives on your machine.
- **Not a web scraper or RAG-over-HTML tool.** If a package doesn't publish `llms.txt` (directly or derivably), that's a miss -- we don't reconstruct docs from rendered pages.
- **Not a general crawler.** Discovery starts from declared dependencies, never from arbitrary URLs or repo trees.
- **Not an ecosystem platform.** One bet -- dep-driven `llms.txt` discovery -- not a marketplace of doc sources.

## Related Work

- **[The `/llms.txt` proposal](https://llmstxt.org/)** -- the convention this builds on: a Markdown file (`llms.txt` + `llms-full.txt`) that gives LLMs a curated, inference-time view of a site's docs. llmsdottxt-mcp is a consumer of this standard, not a competitor to it; it exists to deliver the format to agents at the point of work. Adoption is already real ([Stripe, Vercel, and Anthropic](https://www.semrush.com/blog/llms-txt/) publish it).
- **[Context7](https://github.com/upstash/context7)** -- a hosted MCP server that injects version-specific docs from a central index of 100k+ libraries at query time. It's catalog-first (a library must be indexed by Upstash) and cloud-hosted with an API key; llmsdottxt-mcp is manifest-first and local -- it works from the exact dependency set you have, including the long tail no central index ranks.
- **[GitMCP](https://github.com/idosal/git-mcp)** -- turns any GitHub repo into an MCP server by swapping `github.com` → `gitmcp.io`, reading that repo's `llms.txt`/README. It shares the `llms.txt`-native instinct but is per-repo and URL-driven: you point it at one project at a time. llmsdottxt-mcp inverts that -- it starts from *your* dependency graph and resolves many packages at once, with no URL to paste.

<critical>
- One idea per repo. This is the only `IDEA.md`; the thesis above governs every change.
- Manifest-driven discovery is the bet. If a change adds value without serving dep-driven `llms.txt` discovery, it doesn't belong here.
</critical>
