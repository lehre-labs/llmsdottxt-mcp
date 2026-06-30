# Context Map

## Contexts

- [llmsdottxt-mcp Domain](./src/llmsdottxt_mcp/CONTEXT.md) -- canonical domain language shared across the server.
- [Models](./src/llmsdottxt_mcp/models/CONTEXT.md) -- typed domain, persisted, and response shapes.
- [Config](./src/llmsdottxt_mcp/config/CONTEXT.md) -- settings, constants, and logging language.
- [Scanners](./src/llmsdottxt_mcp/scanners/CONTEXT.md) -- dependency manifest scanning language.
- [Resolvers](./src/llmsdottxt_mcp/resolvers/CONTEXT.md) -- package-registry → docs URL language.
- [Platforms](./src/llmsdottxt_mcp/platforms/CONTEXT.md) -- documentation platform detection language.
- [Tools](./src/llmsdottxt_mcp/tools/CONTEXT.md) -- FastMCP tool wrapper language.
- [Resources](./src/llmsdottxt_mcp/resources/CONTEXT.md) -- read-only `llmstxt://` resource language.
- [Prompts](./src/llmsdottxt_mcp/prompts/CONTEXT.md) -- reusable documentation-workflow prompt language.

## Relationships

- **Domain → Models**: domain terms (Dependency, DocsInfo, Index Entry) are encoded as typed models.
- **Scanners → Models**: scanners produce `Dependency` objects; they do not fetch.
- **Resolvers → Models**: resolvers turn a package name into `DocsInfo`; one resolver per Ecosystem.
- **Platforms → Models**: detectors produce a `PlatformHint`; one detector per Platform.
- **Pipeline → (Scanners, Resolvers, Platforms, Fetcher, Index)**: the orchestrator; nothing else combines them.
- **Tools → (Pipeline, Index)**: tools delegate behavior and return response models; they never fetch directly.
- **Resources → Index**: read-only `llmstxt://` projections of the index.
- **All HTTP → http**: resolvers, platforms, and fetcher request through `llmsdottxt_mcp.http`.

## Single-module concerns (no local CONTEXT.md)

`pipeline.py`, `http.py`, `fetcher.py`, `index.py`, `errors.py`, `cli.py` -- see the [domain context](./src/llmsdottxt_mcp/CONTEXT.md) and root [`AGENTS.md`](./AGENTS.md).
