"""Async HTTP fetcher and parser for llms.txt / llms-full.txt content."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

import httpx
from markdown_it import MarkdownIt
import structlog

from llmsdottxt_mcp import http
from llmsdottxt_mcp.config import LLMS_FULL_TXT_PATH, LLMS_TXT_PATH, USER_AGENT, settings
from llmsdottxt_mcp.models import Link, LlmsTxtResult, ParsedLlmsTxt, Section

if TYPE_CHECKING:
    from markdown_it.token import Token

    from llmsdottxt_mcp.models import DocsInfo, PlatformHint

logger = structlog.get_logger(__name__)

_MD = MarkdownIt()

_TRUNCATION_NOTE = "\n\n[Content truncated. Use llms.txt for individual page links.]"


def _headers(platform: PlatformHint | None) -> dict[str, str]:
    headers = dict(platform.headers) if platform else {}
    headers.setdefault("User-Agent", USER_AGENT)
    return headers


def _clean_base(url: str | None) -> str:
    """Drop any URL fragment before appending /llms.txt.

    npm homepages are often ``github.com/owner/repo#readme``; naively appending
    ``/llms.txt`` yields ``.../repo#readme/llms.txt`` whose fragment the server
    ignores, so it returns the repo's HTML page instead of a 404.
    """
    return (url or "").split("#", 1)[0].rstrip("/")


def _shares_repo_host(docs_host: str, repository_url: str | None) -> bool:
    """True when the docs host is the same host as the source repository.

    If docs and source share a host, the "docs" URL is really a code-forge repo
    page — GitHub, GitLab, Gitea, Codeberg, SourceHut, or any self-hosted forge —
    whose root never carries a single package's llms.txt. Comparing against the
    repo host the resolver already extracted beats hand-maintaining a forge-domain
    list that can never be exhaustive.
    """
    if not repository_url:
        return False
    return urlsplit(repository_url).netloc.casefold() == docs_host.casefold()


def _candidate_urls(docs_info: DocsInfo, base_urls: list[str], filename: str) -> list[str]:
    """Augment platform/resolver URLs with a host-root fallback.

    The llms.txt convention puts the file at the domain root, but resolvers and
    platform hints often yield a deep path (e.g. ``ai-sdk.dev/docs`` whose
    llms.txt lives at ``ai-sdk.dev/llms.txt``). The root is appended last, and
    skipped when the docs host is a shared code forge (see _shares_repo_host).
    """
    urls = list(base_urls)
    base = _clean_base(docs_info.docs_base_url)
    parts = urlsplit(base)
    if parts.netloc and not _shares_repo_host(parts.netloc, docs_info.repository_url):
        root = f"{parts.scheme}://{parts.netloc}"
        root_url = f"{root}/{filename}"
        if root != base and root_url not in urls:
            urls.append(root_url)
    return urls


def _is_llms_txt(response: httpx.Response, parsed: ParsedLlmsTxt) -> bool:
    """Reject a 200 that is not actually llms.txt (e.g. a repo's HTML page).

    The format is markdown that must start with an H1; an HTML content type or a
    parse yielding neither a title nor any sections means we fetched something
    else (commonly a GitHub/homepage HTML page from a homepage-fallback URL).
    """
    if "html" in response.headers.get("content-type", "").lower():
        return False
    return bool(parsed.title or parsed.sections)


async def fetch_llms_txt(
    docs_info: DocsInfo,
    platform: PlatformHint | None,
    client: httpx.AsyncClient,
) -> LlmsTxtResult | None:
    """Try prioritized llms.txt URLs; parse the first that returns 200."""
    base_urls = (
        platform.llms_txt_urls
        if platform
        else [_clean_base(docs_info.docs_base_url) + LLMS_TXT_PATH]
    )
    urls = _candidate_urls(docs_info, base_urls, LLMS_TXT_PATH[1:])
    headers = _headers(platform)

    for url in urls:
        try:
            response = await http.get(
                client, url, headers=headers, timeout=settings.llms_txt_timeout
            )
        except httpx.HTTPError as exc:
            logger.debug("llms_txt_fetch_failed", url=url, error=str(exc))
            continue
        if response.status_code != 200:
            continue
        parsed = parse_llms_txt(response.text)
        if not _is_llms_txt(response, parsed):
            logger.debug(
                "llms_txt_rejected", url=url, content_type=response.headers.get("content-type", "")
            )
            continue
        return LlmsTxtResult(
            package=docs_info.package,
            ecosystem=docs_info.ecosystem,
            url=url,
            raw_content=response.text,
            parsed=parsed,
            fetched_at=datetime.now(UTC).isoformat(),
            platform=platform.platform if platform else None,
        )
    return None


async def fetch_full_text(
    docs_info: DocsInfo,
    platform: PlatformHint | None,
    client: httpx.AsyncClient,
) -> str | None:
    """Stream llms-full.txt, truncating past ``settings.max_full_text_size``."""
    base_urls = (
        platform.llms_full_txt_urls
        if platform
        else [_clean_base(docs_info.docs_base_url) + LLMS_FULL_TXT_PATH]
    )
    urls = _candidate_urls(docs_info, base_urls, LLMS_FULL_TXT_PATH[1:])
    headers = _headers(platform)
    limit = settings.max_full_text_size

    for url in urls:
        try:
            async with http.stream(
                client, url, headers=headers, timeout=settings.full_text_timeout
            ) as response:
                if response.status_code != 200:
                    continue
                chunks: list[str] = []
                total = 0
                async for chunk in response.aiter_text():
                    total += len(chunk.encode())
                    if total > limit:
                        chunks.append(chunk[: limit - (total - len(chunk.encode()))])
                        chunks.append(_TRUNCATION_NOTE)
                        break
                    chunks.append(chunk)
                return "".join(chunks)
        except httpx.HTTPError as exc:
            logger.debug("llms_full_fetch_failed", url=url, error=str(exc))
            continue
    return None


def parse_llms_txt(raw: str) -> ParsedLlmsTxt:
    """Parse the llms.txt markdown format into a structured model.

    Uses markdown-it-py for proper heading-level and code-block awareness.
    """
    tokens = _MD.parse(raw)
    result = ParsedLlmsTxt()

    in_blockquote = False
    sections: list[Section] = []
    current: Section | None = None

    for i, tok in enumerate(tokens):
        if tok.type == "blockquote_open":
            in_blockquote = True
            continue
        if tok.type == "blockquote_close":
            in_blockquote = False
            continue

        if tok.type == "heading_open":
            current = _handle_heading(tokens, i, result, sections)
            continue

        if tok.type == "paragraph_open":
            inline = next((t for t in tokens[i + 1 : i + 3] if t.type == "inline"), None)
            if inline is None:
                continue
            if in_blockquote and result.description is None:
                result.description = inline.content.strip()
                continue
            if current is not None:
                link = _extract_link(inline)
                if link:
                    current.links.append(link)

    result.sections = sections
    return result


def _handle_heading(
    tokens: list[Token], i: int, result: ParsedLlmsTxt, sections: list[Section]
) -> Section | None:
    tag = tokens[i].tag
    inline_tok = tokens[i + 1]
    text = inline_tok.content if inline_tok.type == "inline" else ""

    if tag == "h1":
        result.title = text
        return None

    level = int(tag[1])
    section = Section(name=text, level=level, optional=text.lower().startswith("optional"))
    sections.append(section)
    return section


def _extract_link(inline: Token) -> Link | None:
    """Extract a Link from an inline token if it contains a link_open/link_close pair."""
    if not inline.children:
        return None
    link_idx = next(
        (j for j, c in enumerate(inline.children) if c.type == "link_open"),
        None,
    )
    if link_idx is None:
        return None
    link_open = inline.children[link_idx]
    text_tokens: list[str] = []
    desc_parts: list[str] = []
    past_link = False
    for j in range(link_idx, len(inline.children)):
        c = inline.children[j]
        if c.type == "link_close":
            past_link = True
            continue
        if c.type == "text":
            if past_link:
                desc_parts.append(c.content)
            else:
                text_tokens.append(c.content)
    title = "".join(text_tokens).strip()
    if not title:
        return None
    description = "".join(desc_parts).strip().lstrip(":")
    description = description.strip() or None
    href = link_open.attrGet("href")
    return Link(
        title=title,
        url=str(href) if href else "",
        description=description,
    )
