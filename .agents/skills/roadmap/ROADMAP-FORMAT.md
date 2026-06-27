# ROADMAP-FORMAT.md

## Sections

```
## Done (v0.x)

- [x] item
- [x] item

## Now

- [ ] item
- [ ] item

## Next

- [ ] item
- [ ] item

## Non-goals

- item
- item
```

## Conventions

- **Done**: completed items. Keep in rough chronological order (most recent at bottom). Version-group when a release exists: `## Done (v0.1)`, `## Done (v0.2)`.
- **Now**: actively in flight or queued for immediate work. Cap at ~5 items.
- **Next**: confirmed direction but not yet started. No cap, but prefer small over big.
- **Non-goals**: explicit exclusions to prevent scope creep. Only add items that someone might reasonably expect or has asked about before.

### Item format

```
- [ ] Concrete, deliverable description — [x] or [ ] status marker
```

- Every item must be a concrete, deliverable unit of work — not a theme, not a mantra.
- Prefer "Add `cache-ttl-seconds` config option" over "Improve caching."
- No dates, assignees, issue links, or ETA estimates.
- No nested sub-lists or hierarchies.

## Authoring

Prefer the `/roadmap` skill for all edits. Manual edits to this file should follow the same conventions.

## Non-goal

This format is for a single-person, pre-1.0 open-source project. It intentionally avoids milestones, quarters, tracking tables, and GitHub issue links. Add those when the project grows past maintainable simplicity.
