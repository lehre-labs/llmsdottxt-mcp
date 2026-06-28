# llms.txt Parser in JavaScript

> Converted from HTML — upstream has no `.md` variant.
> Source: <https://llmstxt.org/llmstxt-js.html>

This page demonstrates a JavaScript implementation of the llms.txt parser. The
original page runs the parser live in the browser and renders its output; the
reference implementation and sample input/output are reproduced below.

## Parser

```javascript
function parseLLMsTxt(txt) {
    function parseLinks(links) {
        const linkPat = /-\s*\[(?<title>[^\]]+)\]\((?<url>[^\)]+)\)(?::\s*(?<desc>.*?))?$/gm;
        return Array.from(links.matchAll(linkPat)).map(match => match.groups);
    }

    const [start, ...rest] = txt.split(/^##\s*(.*?)$/m);
    const sections = Object.fromEntries(
        Array.from({ length: Math.floor(rest.length / 2) }, (_, i) => [
            rest[i * 2],
            parseLinks(rest[i * 2 + 1])
        ])
    );

    const pat = /^#\s*(?<title>.+?$)\n+(?:^>\s*(?<summary>.+?$))?\n+(?<info>.*)/ms;
    const match = start.trim().match(pat);
    const result = { ...match.groups, sections };

    return result;
}
```

## Sample input

```markdown
# Title

> Optional description goes here

Optional details go here

## Section name

- [Link title](https://link_url): Optional link details

## Optional

- [Link title](https://link_url)
```

## Parser output

The input above parses to:

```json
{
  "title": "Title",
  "summary": "Optional description goes here",
  "info": "Optional details go here",
  "sections": {
    "Section name": [
      { "title": "Link title", "url": "https://link_url", "desc": "Optional link details" }
    ],
    "Optional": [
      { "title": "Link title", "url": "https://link_url", "desc": undefined }
    ]
  }
}
```
