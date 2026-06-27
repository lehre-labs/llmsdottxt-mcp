# Consolidated tool surface with hint system over separate list/search/resolve tools

Status: accepted

The v0.1 tool surface exposed five tools (`scan_deps`, `resolve_docs`, `list_packages`, `search_docs`, `status`) plus two resources (`llmstxt://packages`, `llmstxt://package/{e}/{n}`) plus one prompt (`find_docs_for_import`). Each had a single job, but the overlap created confusion: `list_packages` + `search_docs` + `llmstxt://packages` all returned package metadata in slightly different shapes. `resolve_docs` dumped entire llms-full.txt files into context with no navigation support. Agents had to guess which tool to use first.

We chose four tools — `index_deps`, `search`, `browse`, `status` — with one resource plus one prompt. `search` unifies package listing and free-text lookup with an empty query returning all packages. `browse` unifies TOC navigation and section-level content retrieval through a single `section` parameter (absent = TOC, present = section). Each tool carries a hint block in its docstring: what it does, when to use it over another tool, and the natural next action after a result. Hints are embedded in tool descriptions as a `## Using this tool` section that FastMCP surfaces to clients.

## Consequences

Down from eight exposed endpoints to six. Agents follow a linear discovery pattern: `index_deps` → `browse(package)` → `browse(package, section)`. Hints reduce wrong-tool errors at the client level. The trade-off: richer tools have more complex return types, and hint text must be maintained alongside behavior changes.
