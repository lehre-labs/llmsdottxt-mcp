# JSON-file index over SQLite  (superseded by 0004)

The index needs persistence and simple search across a project's dependencies. We chose one JSON file per package under `~/.llms.txt.d/index/{ecosystem}/{name}.json`, with gzip-cached `llms-full.txt` and a `meta.json`, using ranked substring matching over metadata instead of SQLite.

## Consequences

Zero-dependency, human-inspectable, works fine to ~200 packages. SQLite remains a future option if scale demands it.
