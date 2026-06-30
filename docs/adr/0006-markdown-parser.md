# markdown-it-py section parsing over regex

Status: accepted

`parse_llms_txt()` currently uses three hand-rolled regexes (`_H1`, `_H2`, `_LINK`) to extract headings and links from llms.txt. This works for the well-formed format but silently produces invalid results when markdown contains indented headings, headings inside fenced code blocks, or HTML comments. Section-level chunking of llms-full.txt (dropping truncation) needs H1–H6 parsing with correct nesting and code-block awareness. Extending the regex approach to handle all six heading levels plus code-fence detection would re-implement a fraction of a real parser poorly.

We chose `markdown-it-py` -- already a transitive dependency through Rich at version 4.2.0. It emits a flat token stream with `heading_open`/`heading_close` and `fence`/`code_block` markers, plus `inline` tokens for link text/URL pairs. Walking the token stream builds a heading tree for any depth, correctly skipping headings inside fenced blocks. No new dependency.

## Consequences

llms.txt and llms-full.txt both use the same parser. Section chunking works for any heading depth. Parse errors are visible rather than silently wrong. The trade-off: the parser is heavier than three regexes (though already in the dependency graph), and the token-walking code replaces 18 lines of regex with ~40 lines of tree building.
