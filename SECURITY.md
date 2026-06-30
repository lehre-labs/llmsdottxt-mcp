# Security Policy

## Supported Versions

This project is pre-1.0. Only the latest released version receives security fixes.

## Reporting Vulnerabilities

Do not open a public issue. Use GitHub private vulnerability reporting:

```text
https://github.com/lehre-labs/llmsdottxt-mcp/security/advisories/new
```

Include the affected version or commit, reproduction steps, and expected impact.

## Security Boundaries

- All fetched `llms.txt` / `llms-full.txt` content is untrusted: fetched over http(s) only, size-capped, never executed.
- All HTTP goes through `llmsdottxt_mcp.http` for retry and rate-limiting; document bodies are never logged.
- The cache under `~/.llms.txt.d/` holds third-party docs -- it is gitignored and must never be committed.
- stdout is the MCP stdio channel; library code never prints. Logs are JSON on stderr.
