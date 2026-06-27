---
name: roadmap
description: Maintain ROADMAP.md — finish shipped items, request new ones, or defer stale ones.
metadata:
  author: lehre-labs
  version: "0.1.0"
---

# Roadmap

Use `/roadmap finish|request|defer` to update `ROADMAP.md` with a single-item change.
See `ROADMAP-FORMAT.md` for the section structure and conventions.

## Actions

### `/roadmap finish "<item>"`

Move an item from **Now** or **Next** into **Done**.
If the item spans multiple sub-items, list each one.

1. Find the item in Now or Next.
2. Cut it from that section.
3. Paste it into Done, preserving the `- [x]` marker.
4. Keep Done in rough chronological order (most recent at bottom).

### `/roadmap request "<item>" {now|next}`

Add a new item to **Now** or **Next**.

1. Confirm the item is concrete and deliverable.
2. Add `- [ ] <item>` to the chosen section.
3. If adding to Now, keep it under ~5 items to avoid sprawl.

### `/roadmap defer "<item>"`

Remove an item from **Now** or **Next** — it's no longer planned.

1. Find and remove the exact line from Now or Next.
2. Optionally add it to **Non-goals** if the decision is worth recording.

## Guardrails

- One item per action. Batch only when the user explicitly asks.
- Never add items without explicit user request.
- Keep Now items scoped to what one person could deliver in a few focused sessions.
- Do not add dates, assignees, issue links, or ETA estimates unless asked.
