# Engineering Rules

Concrete, checkable constraints for llmsdottxt-mcp. `AGENTS.md` holds the principles; this is the project-specific detail they operate on.

## Layered architecture

Imports flow downward only (enforced by `import-linter` -- `uv run lint-imports`):

```
cli -> server -> tools / resources / prompts -> pipeline
    -> scanners / resolvers / platforms / fetcher / index -> http -> config / errors -> models
```

- `pipeline` is the single orchestrator that wires the discovery layer.
- `resolvers/`, `platforms/`, `scanners/` are registry packages -- add an ecosystem or platform by dropping a module in and registering it via the package's `registry.py`.

## Typed boundaries

- Aliases and finite enums live in `models/strings.py`: `StrEnum` for protocol values (`Ecosystem`, `Platform`, `DocsUrlSource`), a `Literal` for `LogLevel`.
- Pydantic over `dict[str, Any]`. Models split by role: `core.py` (domain), `index.py` (persisted), `responses.py` (tool-facing), `strings.py` (aliases/enums).
- Validate tool inputs strictly (`PackageName`, `SearchQuery`); keep fetched docs tolerant.
- Field and tool-return types must be importable at runtime, not under `TYPE_CHECKING`.
- External docs (this project's own dogfood): Pydantic `https://pydantic.dev/llms.txt`, FastMCP `https://gofastmcp.com/llms.txt`.

## MCP contracts

- Tools stay thin: validate the signature, then delegate to `pipeline`/`index`. Return Pydantic models; docstrings drive agent routing.
- Convert internal errors to `fastmcp.exceptions.ToolError` at the boundary.
- Read-only context = `llmstxt://` resources; actions = tools.

## Observability & safety

- stdout is the MCP stdio channel -- never `print()` in library code; logs are JSON on stderr via `structlog`. Exception: `cli.py` prints tab-separated rows via plain `print()` (no Rich tables).
- Route all HTTP through `llmsdottxt_mcp.http` (`get`/`stream`); one shared `AsyncClient` per scan. `get` retries transient errors (incl. 429/503, honoring `Retry-After`) and raises `BlockedByChallengeError` on an unsolvable WAF challenge -- the pipeline counts those as `blocked`, not `missing`.
- Fetched llms.txt is untrusted: http(s) only, cap size (`settings.max_full_text_size`), never execute. Log URLs and sizes, never bodies. The `~/.llms.txt.d/` cache is gitignored -- never commit it.

## Testing

- `pytest` (+ `pytest-xdist -n auto`, `pytest-cov`), `pytest-httpx` to mock docs hosts, `hypothesis` for pure helpers. Tests mirror `src/`.
- Reproduce a bug with a failing test before fixing it. No live network in unit tests -- use the `live` marker. Rely on the autouse `tmp_index` fixture. Stay above the `fail_under` coverage gate.

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
