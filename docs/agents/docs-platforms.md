# Documentation Platforms

llmsdottxt-mcp auto-discovers and fetches `/llms.txt` and `/llms-full.txt` from dependency docs. Platform detection enables optimized fetches; all standards-compliant platforms work via generic fallback.

## Legend

- [x] Auto-detected, optimized headers/URLs
- [~] Supported via generic `/llms.txt` fallback (any standards-compliant platform)
- [ ] Planned, not yet implemented

## Hosted Documentation Platforms

| Platform | Status | Auto llms.txt | llms-full.txt | .md pages | Details |
|----------|--------|---------------|---------------|-----------|---------|
| [Mintlify](https://mintlify.com) | [x] | Yes | Yes | Yes | X-Llms-Txt header, well-known paths |
| [Fern](https://buildwithfern.com) | [~] | Yes | Yes | Yes | Bot-specific markdown serving |
| [GitBook](https://gitbook.com) | [x] | Yes | Yes | Yes | `.gitbook.io` URL + body marker |
| [ReadMe](https://readme.com) | [x] | Yes (toggle) | No | Yes (.md suffix) | `.readme.io` URL pattern |
| [Redocly](https://redocly.com) | [x] | Yes (toggle) | No | No | `.redoc.ly` URL pattern |

## Static Site Generator Plugins

| Framework | Plugin | Status | llms.txt | llms-full.txt | .md |
|-----------|--------|--------|----------|---------------|-----|
| [Docusaurus](https://docusaurus.io) | [docusaurus-plugin-llms](https://github.com/rachfop/docusaurus-plugin-llms) | [x] | Yes | Yes | Yes |
| Read the Docs | [sphinx-llms-txt](https://sphinx-llms-txt.readthedocs.io) | [x] | Yes | Yes | No |
| [Astro Starlight](https://starlight.astro.build) | [starlight-llms-txt](https://github.com/delucis/starlight-llms-txt) | [~] | Yes | Yes | Yes |
| [MkDocs](https://mkdocs.org) | [mkdocs-llmstxt](https://github.com/pawamoy/mkdocs-llmstxt) | [x] | Yes | Yes | No | Generator meta + body marker |
| [VitePress](https://vitepress.dev) | [vitepress-plugin-llms](https://github.com/okineadev/vitepress-plugin-llms) | [~] | Yes | Yes | Yes |
| [Hugo](https://gohugo.io) | Custom output format | [~] | Yes | Manual | No |
| [Eleventy](https://11ty.dev) | [eleventy-plugin-llms-txt](https://github.com/CleverCloud/eleventy-plugin-llms-txt) | [ ] | Yes | No | No |
| [Gatsby](https://gatsbyjs.com) | [gatsby-plugin-llms-txt](https://www.gatsbyjs.com/plugins/gatsby-plugin-llms-txt/) | [ ] | Yes | No | No |

## Standalone Generators

Not platforms, but useful for manual setup.

- [llmstxt.new](https://llmstxt.new) (Firecrawl) -- crawls any URL, AI-generates both files. Open source.
- [Mintlify Generator](https://llms-txt-generator.mintlify.review/) -- paste URL, generates starter from site structure. Free.
- [LLMTEXT](https://parallel.ai/blog/LLMTEXT-for-llmstxt) (Parallel.ai) -- sitemap-based, includes validator. Open source.

## CMS Plugins

| Platform | Plugin | Status |
|----------|--------|--------|
| WordPress | Yoast SEO, "Website LLMs.txt", "LLMs.txt for WP" | [ ] |
| Shopify | "LLMs.txt Generator" app | [ ] |

## Adding Detection

To add platform detection (promoting from [~] to [x]):

1. Add the enum value in `src/llmsdottxt_mcp/models/strings.py` (`Platform`).
2. Create a `BasePlatform` subclass in `src/llmsdottxt_mcp/platforms/` -- override `from_response` and/or `from_url`.
3. Register it in `src/llmsdottxt_mcp/platforms/registry.py` at the right priority position.
4. Add tests in `tests/test_platforms.py` following the `httpx_mock` pattern.

Generic fallback works for all platforms that serve `/llms.txt`.
