"""Response-model serialization tests (token-trim behavior)."""

from __future__ import annotations

from pydantic import TypeAdapter
import pydantic_core

from llmsdottxt_mcp.models import (
    BrowseToc,
    Ecosystem,
    Link,
    PackageSummary,
    ParsedLlmsTxt,
    Section,
)


def test_summary_omits_none_and_default_fields() -> None:
    data = pydantic_core.to_jsonable_python(PackageSummary(package="x", ecosystem=Ecosystem.python))
    # Required fields stay; None/default fields are dropped to save tokens.
    assert data == {"package": "x", "ecosystem": "python"}


def test_browse_toc_trims_nested_sections_and_links() -> None:
    toc = BrowseToc(
        package="p",
        ecosystem=Ecosystem.node,
        title="P",
        sections=[
            Section(name="Docs", links=[Link(title="Intro", url="u")]),
            Section(name="Empty"),
        ],
    )
    data = pydantic_core.to_jsonable_python(toc)
    # Link without a description drops it; default level/optional/links are gone.
    assert data["sections"] == [
        {"name": "Docs", "links": [{"title": "Intro", "url": "u"}]},
        {"name": "Empty"},
    ]
    assert "description" not in data  # None dropped
    assert "has_full_text" not in data  # default False dropped


def test_trim_keeps_output_schema_intact() -> None:
    # The serializer must not collapse the per-field serialization schema:
    # FastMCP builds output_schema from json_schema(mode="serialization").
    schema = TypeAdapter(PackageSummary).json_schema(mode="serialization")
    assert schema["required"] == ["package", "ecosystem"]
    assert "version" in schema["properties"]
    assert "full_text_size" in schema["properties"]


def test_section_persistence_round_trips() -> None:
    parsed = ParsedLlmsTxt(
        title="T",
        sections=[Section(name="S", links=[Link(title="a", url="b")])],
    )
    restored = ParsedLlmsTxt.model_validate_json(parsed.model_dump_json())
    assert restored == parsed
    # Defaults dropped on the wire are restored on load.
    assert restored.sections[0].level == 2
    assert restored.sections[0].optional is False
