#!/usr/bin/env bash
# hitl-loop.template.sh — Human-in-the-Loop diagnostic loop template
#
# Replace the placeholder commands with your actual test/check commands.
# The loop exits when the command succeeds (exit code 0) or you press Ctrl+C.

set -euo pipefail

REPRO_COMMAND="REPLACE_ME_WITH_YOUR_REPRO_COMMAND"

echo "🔁 HITL diagnostic loop"
echo "  Command: $REPRO_COMMAND"
echo "  Press Ctrl+C to exit"
echo ""

while true; do
  echo "--- Running at $(date '+%H:%M:%S') ---"

  if $REPRO_COMMAND 2>&1; then
    echo "✅ Command succeeded! Exiting loop."
    exit 0
  fi

  echo ""
  echo "💡 Make a change, then press Enter to re-run (Ctrl+C to exit)"
  read -r
done
