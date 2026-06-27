---
name: mcp-contracts
description: FastMCP contract guidance.
globs: ["src/llmstxt_mcp/tools/**/*.py", "src/llmstxt_mcp/resources/**/*.py", "src/llmstxt_mcp/prompts/**/*.py", "src/llmstxt_mcp/server.py"]
---
- Keep tools thin: validate the signature, then delegate to `pipeline` or `index`.
- Return structured Pydantic models; write docstrings for agent routing.
- Separate read-only context (`llmstxt://` resources) from actions (tools).
- Convert internal errors to `fastmcp.exceptions.ToolError` at the tool boundary.
- Register by domain through each package's `registry.py`.
