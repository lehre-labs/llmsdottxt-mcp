# Token-trimmed tool responses via a Pydantic model serializer

Status: accepted

MCP tool returns become `structuredContent` on the wire, and FastMCP serializes them with `pydantic_core.to_jsonable_python(...)`, which by default emits every field — including `None` and values still at their default. For `search` listings and `browse` table-of-contents trees (many `Section`/`Link` rows) this inflates the agent's context with `"description": null`, `"has_full_text": false`, `"level": 2`, and empty lists. TOON and other non-JSON encodings were considered and rejected: MCP clients expect standard structured JSON, so the payload must stay valid JSON that matches the tool's `output_schema`.

We chose a `TrimmedModel` base that defines a `@model_serializer(mode="wrap")` dropping keys whose value is `None` or equal to the field's default; the response models (`ScanReport`, `PackageSummary`, `SearchHit`, `BrowseToc`, `StatusReport`) and the nested `Link`/`Section` inherit it. Because every trimmed field carries a default, it stays non-required in the schema, so omitting it from the payload remains schema-valid. The serializer method deliberately has **no return type annotation**: annotating it (even as `Any` or `dict[str, Any]`) makes Pydantic generate an empty serialization JSON schema, which would erase FastMCP's per-field `output_schema` (FastMCP builds it from `json_schema(mode="serialization")`).

## Consequences

Smaller, cheaper payloads with no change to the public schema or field names, and the same trim shrinks the JSON persisted in the index (defaults round-trip back on load). The trade-offs: a field set explicitly to its default is indistinguishable from one omitted (acceptable — absence means default), and the missing return annotation is load-bearing, so it carries a comment to stop a future "add a type hint" cleanup from silently flattening the output schema.
