# Resolvers Context

Package-registry → docs URL language.

## Language

**Resolver**:
A `BaseResolver` subclass that maps a package name to `DocsInfo` for one Ecosystem.
_Avoid_: handler, client, fetcher

**Resolver Registry**:
The per-Ecosystem resolver map. `get_resolver(ecosystem)` returns the right resolver; `resolve(package, ecosystem, client)` does the full lookup.
_Avoid_: resolver map, registry lookup

**Docs URL Source**:
An enum (`DocsUrlSource`) capturing where the docs URL was found: custom project URLs, registry documentation field, homepage fallback, or none.
_Avoid_: source, origin, provenance
