#!/usr/bin/env bash
set -euo pipefail

payload=$(cat)
file_path=$(jq -r '.tool_input.file_path // ""' <<<"$payload")

[[ "$file_path" == *.py ]] || exit 0
[[ -f "$file_path" ]] || exit 0

root=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
output=$(cd "$root" && ruff check "$file_path" --output-format concise 2>&1) || true

# Concise format emits "All checks passed!" on clean — skip.
# On issues, lines look like: file:1:1: E401 [*] Multiple imports on one line
grep -qE '[A-Z]+[0-9]+ ' <<<"$output" || exit 0

# Strip footer ("Found N errors", "[*] N fixable…")
output=$(sed '/^Found [[:digit:]]/,$d' <<<"$output")

jq -n --arg out "$output" '{
  systemMessage: "ruff: issues",
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    additionalContext: ("ruff\n" + $out)
  }
}'
