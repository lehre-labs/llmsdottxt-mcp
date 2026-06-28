# llmstxt.org spec mirror

Local copy of the canonical [llms.txt specification](https://llmstxt.org/) — the
protocol this project implements. Stored in-repo (rather than just linked) because
it is the **core domain reference**: scanners, the fetcher, and the llms.txt parse
tree all derive their shape from it. `.d` mirrors the project's own
`~/.llms.txt.d/` index convention.

Snapshot fetched from `https://llmstxt.org/` — exact timestamp, http status, size,
sha256, etag, and last-modified per file are recorded in
[`metadata.json`](./metadata.json). Re-fetch with [`fetch.sh`](./fetch.sh) when the
spec changes; cross-reference [`../../agents/source-map.md`](../../agents/source-map.md)
(row: *llms.txt spec*).

## Contents

| File | Title | Upstream |
|---|---|---|
| [`index.md`](./index.md) | The /llms.txt file (the spec) | <https://llmstxt.org/index.md> |
| [`intro.html.md`](./intro.html.md) | `llms-txt` Python module & CLI | <https://llmstxt.org/intro.html.md> |
| [`core.html.md`](./core.html.md) | `llms-txt` Python source (literate) | <https://llmstxt.org/core.html.md> |
| [`ed-commonmark.md`](./ed-commonmark.md) | Example llms.txt (`ed` editor) | <https://llmstxt.org/ed-commonmark.md> |
| [`domains-commonmark.md`](./domains-commonmark.md) | llms.txt in different domains | <https://llmstxt.org/domains-commonmark.md> |
| [`nbdev.md`](./nbdev.md) | Helping LLMs understand an nbdev project | <https://llmstxt.org/nbdev.md> |
| [`llmstxt-js.md`](./llmstxt-js.md) | JS parser reference (**converted from HTML**) | <https://llmstxt.org/llmstxt-js.html> |

> `llmstxt-js.html` has no `.md` variant upstream, so it was converted from HTML to
> markdown by hand — prose, parser source, and sample I/O preserved verbatim.

## Re-fetch

```sh
docs/references/llmstxt.org.d/fetch.sh
```

This overwrites the `*.md` copies, refreshes [`metadata.json`](./metadata.json), and
warns if `llmstxt-js.html` changed upstream (its `.md` is hand-converted — re-convert
from `llmstxt-js.html` when flagged, since there is no upstream `.md`).
