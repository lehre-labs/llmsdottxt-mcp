---
name: cli-output
description: Line-oriented, fzf-friendly CLI output.
globs: ["src/llmsdottxt_mcp/cli.py"]
---
- CLI commands print machine-readable rows, not Rich tables. Box-drawing tables are not fzf/grep/awk-friendly for computer use.
- Emit list/tabular data as one record per line, tab-separated, via plain `print()` (cli.py is exempt from the `T20` print ban). Plain `print` keeps tabs literal and never soft-wraps — Rich `Console.print` expands tabs to spaces and wraps at the terminal width, which corrupts delimited output.
- Human-oriented summary lines may use the Rich `Console` (it auto-strips styling when stdout is piped); never use `rich.table.Table` for the CLI entry point.
- The MCP stdio channel still forbids `print()` everywhere else — this exemption is scoped to `cli.py`, which is never the MCP transport.
