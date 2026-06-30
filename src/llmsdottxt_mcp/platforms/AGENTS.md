# Platforms Package

Detect the documentation Platform and produce prioritized llms.txt URLs + optimizations.

## Conventions

- Add a platform: subclass `BasePlatform`, implement `from_response` and/or `from_url`, build the hint with `cls.hint(...)`, and register it in `PLATFORM_REGISTRY`.
- Detection probes the **homepage** (base URL) -- platform fingerprints (e.g. Mintlify's `x-llms-txt` / `x-mint-proxy-version` headers) live there, not on the plain-text `/llms.txt`.

## Gotchas

- Custom domains hide `.mintlify.`; rely on response headers, not just the URL.

## Out Of Scope

- Fetching/parsing content, resolving packages.
