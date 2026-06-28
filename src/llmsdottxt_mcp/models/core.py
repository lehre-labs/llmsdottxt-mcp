"""Core domain models shared across the discovery pipeline."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, SerializerFunctionWrapHandler, model_serializer

from llmsdottxt_mcp.models.strings import DocsUrlSource, Ecosystem, Platform


class TrimmedModel(BaseModel):
    """Base model whose JSON serialization omits ``None`` values and fields left
    at their default.

    Shrinks the structured-content payloads FastMCP sends to clients (it
    serializes returns via ``pydantic_core.to_jsonable_python``) and the
    gzip-free JSON persisted in the index. Omitted fields all carry defaults, so
    they stay non-required in the generated schema and the output remains valid.

    The serializer deliberately has **no return annotation**: annotating it
    (even as ``Any``) makes Pydantic emit an empty serialization JSON schema,
    which would erase FastMCP's per-field ``output_schema``.
    """

    @model_serializer(mode="wrap")
    def _omit_defaults(self, handler: SerializerFunctionWrapHandler):
        data = handler(self)
        kept: dict[str, Any] = {}
        for name, field in type(self).model_fields.items():
            key = field.alias or name
            if key not in data:
                continue
            value = data[key]
            if value is None:
                continue
            if not field.is_required() and value == field.get_default(call_default_factory=True):
                continue
            kept[key] = value
        return kept


class Dependency(BaseModel):
    """A direct dependency extracted from a project manifest."""

    name: str
    version_spec: str | None = None
    ecosystem: Ecosystem


class DocsInfo(BaseModel):
    """Resolved documentation location for a package."""

    package: str
    ecosystem: Ecosystem
    docs_base_url: str | None = None
    docs_url_source: DocsUrlSource = DocsUrlSource.none
    repository_url: str | None = None
    original_homepage: str | None = None
    latest_version: str | None = None


class PlatformHint(BaseModel):
    """Platform detection result with prioritized URLs and optimizations."""

    platform: Platform | None = None
    llms_txt_urls: list[str] = Field(default_factory=list)
    llms_full_txt_urls: list[str] = Field(default_factory=list)
    per_page_md_pattern: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)


class Link(TrimmedModel):
    """A single link entry inside an llms.txt section."""

    title: str
    url: str
    description: str | None = None


class Section(TrimmedModel):
    """An H2-H6 heading group of links in an llms.txt file."""

    name: str
    level: int = 2
    optional: bool = False
    links: list[Link] = Field(default_factory=list)


class ParsedLlmsTxt(BaseModel):
    """Structured parse of an llms.txt file."""

    title: str = ""
    description: str | None = None
    sections: list[Section] = Field(default_factory=list)


class LlmsTxtResult(BaseModel):
    """A successfully fetched and parsed llms.txt file."""

    package: str
    ecosystem: Ecosystem
    url: str
    raw_content: str
    parsed: ParsedLlmsTxt
    fetched_at: str
    platform: Platform | None = None
