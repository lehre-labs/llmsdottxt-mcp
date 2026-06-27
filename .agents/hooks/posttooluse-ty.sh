#!/usr/bin/env bash
set -euo pipefail

payload=$(cat)
file_path=$(jq -r '.tool_input.file_path // ""' <<<"$payload")

[[ "$file_path" == *.py ]] || exit 0
[[ -f "$file_path" ]] || exit 0

root=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
output=$(cd "$root" && uv run ty check "$file_path" --output-format concise 2>&1) || true

# Concise format: file:line:col: error: message
grep -qE '^[^ ]+:[0-9]+:[0-9]+:' <<<"$output" || exit 0

jq -n --arg out "$output" '{
  systemMessage: "ty: issues",
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    additionalContext: ("ty\n" + $out)
  }
}'
