# Index Context

SQLite index and full-text cache language.

## Language

**Index Entry**:
One package's persisted row in the `index_entry` table. Has ecosystem, package name, version info, docs URLs, platform, full-text metadata, and the serialized `llms.txt`.
_Avoid_: record, row, doc, cache entry

**FTS5**:
SQLite's built-in full-text search engine. The `index_entry_fts` virtual table holds searchable text extracted from package names, `llms.txt` titles, section names, and link titles/descriptions.
_Avoid_: search index, text index

**Index Meta**:
Key/value metadata about the index itself -- version, last scan timestamp, project root, ecosystem list, package counts. Persisted in the `index_meta` table.
_Avoid_: index config, index settings, metadata

**Full-Text Cache**:
Gzip-compressed `llms-full.txt` stored on disk at `~/.llms.txt.d/cache/<ecosystem>/<package>__llms-full.txt.gz`. Used to serve full docs without re-fetching.
_Avoid_: full-text store, doc cache, content cache

**Migration**:
A numbered SQL script in `_connection._MIGRATIONS` that transforms the index schema. Run in order on first connect; the current version is tracked in `index_meta`.
_Avoid_: schema upgrade, version bump
