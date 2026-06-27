# Config Context

Settings, constants, and logging language.

## Language

**Settings**:
Project configuration loaded from `LLMSTXT_*` env vars and `.env`. Controls index location, cache directory, concurrency, size caps, timeouts, and log level.
_Avoid_: options, preferences, env config

**Constants**:
Hardcoded protocol paths (`/llms.txt`, `/.well-known/llms.txt`), header templates (`USER_AGENT`), and platform-specific markers (Mintlify headers).
_Avoid_: defaults, globals, literals

**Logging**:
Structured JSON logging to stderr via `structlog`, with level gated by the configured `log_level`.
_Avoid_: print output, console, logger
