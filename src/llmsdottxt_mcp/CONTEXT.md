# llmsdottxt-mcp Domain

Canonical domain language for the server. Every concept has one name.

## Language

**Dependency**:
A direct dependency extracted from a project manifest. Has name, optional version spec, Ecosystem.
_Avoid_: requirement, package ref, import

**Ecosystem**:
A package universe: `python`, `node`, `rust`, `go`. A `StrEnum`.
_Avoid_: language, registry type

**DocsInfo**:
The resolved documentation location for a package (docs base URL, source, repository, latest version).
_Avoid_: doc meta, package info

**Platform**:
A documentation hosting service we can optimize for: mintlify, readthedocs, docusaurus, github_pages.
_Avoid_: host, provider, vendor

**PlatformHint**:
Detection result with prioritized `llms.txt` / `llms-full.txt` URLs and per-platform optimizations.
_Avoid_: platform config

**llms.txt**:
The standard index file a docs site exposes (title, description, H1-H6 sections of links).
_Avoid_: doc index, manifest

**llms-full.txt**:
The full concatenated documentation text; may be large and is cached gzipped.
_Avoid_: full docs, dump

**Page**:
One documentation page inside an llms-full.txt, delimited by an H1 heading (`# Title`); `browse(package, section)` slices the full text to the Page whose title matches the `section` argument.
_Avoid_: chunk, article, doc

**Section / Link**:
An H2-H6 heading-delimited group (Section, with level tracking) of `- [Title](url): desc` entries (Link) in an llms.txt.
_Avoid_: group, item

**Index Entry**:
One package's persisted row in the SQLite index at `~/.llms.txt.d/index.db`.
_Avoid_: record, doc, cache entry

**Scan**:
The pipeline run that turns a project's Dependencies into Index Entries.
_Avoid_: crawl, build, sync
