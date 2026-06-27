# Agent Source Map

Use this when a dependency, CLI, or protocol detail may have changed. Prefer `llms.txt`.

## Sources

| Concern | Primary source | Fallback |
|---|---|---|
| FastMCP | https://gofastmcp.com/llms.txt | `/llms-full.txt`, then linked `.md` pages |
| MCP protocol | https://modelcontextprotocol.io/llms-full.txt | https://modelcontextprotocol.io/docs |
| llms.txt spec | https://llmstxt.org/ | https://llmstxt.org/index.md |
| Pydantic | https://pydantic.dev/llms.txt | https://docs.pydantic.dev/latest/ |
| pydantic-settings | https://docs.pydantic.dev/latest/concepts/pydantic_settings/ | — |
| httpx | https://www.python-httpx.org/ | https://www.python-httpx.org/async/ |
| Typer | https://typer.tiangolo.com/ | No llms.txt as of 2026-06-27; use HTML docs |
| structlog | https://www.structlog.org/en/stable/ | https://www.structlog.org/en/stable/standard-library.html |
| tenacity | https://tenacity.readthedocs.io/en/latest/ | — |
| aiolimiter | https://aiolimiter.readthedocs.io/en/latest/ | — |
| Ruff | https://docs.astral.sh/ruff/llms.txt | explicit `index.md` paths from that index |
| uv | https://docs.astral.sh/uv/llms.txt | explicit `index.md` paths from that index |
| ty | https://docs.astral.sh/ty/llms.txt | explicit `index.md` paths from that index |
| pytest | https://docs.pytest.org/en/stable/ | https://docs.pytest.org/en/stable/contents.html |
| pytest-httpx | https://colin-b.github.io/pytest_httpx/ | — |
| Python 3.14 | https://docs.python.org/3.14/ | https://docs.python.org/3/whatsnew/3.14.html |
| Conventional Commits | https://www.conventionalcommits.org/en/v1.0.0/ | `pyproject.toml` Commitizen config |

## Fetching

- Prefer `llms.txt` when present; for Astral docs use explicit `index.md` paths from the index.
- This project *is* an llms.txt client — dogfood it: `uvx llmstxt-mcp scan` then the `search` tool.
