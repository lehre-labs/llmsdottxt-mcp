---
name: fetch-safety
description: Safety for fetching and caching third-party docs.
globs: ["src/llmstxt_mcp/**/*.py"]
---
- Treat all fetched llms.txt content as untrusted input.
- Only fetch over http(s); cap response size; never execute fetched content.
- The cache under `~/.llms.txt.d/` holds third-party docs — never commit it; it is gitignored.
- Do not log full document bodies; log URLs and sizes.
