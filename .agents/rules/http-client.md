---
name: http-client
description: Shared HTTP transport rules.
globs: ["src/llmsdottxt_mcp/http.py", "src/llmsdottxt_mcp/resolvers/**/*.py", "src/llmsdottxt_mcp/platforms/**/*.py", "src/llmsdottxt_mcp/fetcher.py"]
---
- Route all requests through `llmsdottxt_mcp.http` (`get` / `stream`) for retry + rate-limit.
- Build one shared `AsyncClient` per scan; never one client per request.
- `get` retries transient errors (connect/timeout/5xx **and 429/503**) via tenacity,
  honoring a numeric `Retry-After` (capped at `_MAX_RETRY_AFTER`); `stream` does not retry
  (body consumed once).
- Distinguish a *genuine* 429/503 (retry) from a *bot challenge* (skip). `get` raises
  `BlockedByChallengeError` when it fingerprints an unsolvable WAF — Cloudflare
  (`cf-mitigated`), DataDome, Imperva Incapsula, AWS WAF, Akamai, Sucuri. These never
  pass headless, so retrying is pointless; the pipeline counts them as `blocked`, not
  `missing`. Add a new vendor by extending `_WAF_HEADER_FINGERPRINTS` / `_challenge_vendor`.
- Respect `settings.max_full_text_size` when streaming `llms-full.txt`.
