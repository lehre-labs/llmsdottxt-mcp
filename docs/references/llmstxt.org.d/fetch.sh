#!/usr/bin/env bash
# Fetch the latest llms.txt spec docs from llmstxt.org and record fetch metadata.
#
# Re-run any time the spec may have changed. It overwrites the local *.md copies
# and rewrites metadata.json with per-file http status, size, sha256, etag, and
# last-modified so drift is auditable. The HTML-only page (llmstxt-js.html) has no
# upstream .md; it is fetched for reference and must be re-converted into
# llmstxt-js.md by hand — the script flags it when its sha256 changes.
set -euo pipefail
cd "$(dirname "$0")"

BASE="https://llmstxt.org"
MD_FILES=(index.md intro.html.md core.html.md ed-commonmark.md domains-commonmark.md nbdev.md)
HTML_FILE="llmstxt-js.html"           # no upstream .md -> hand-converted to llmstxt-js.md
META="metadata.json"
TSV="$(mktemp)"
trap 'rm -f "$TSV"' EXIT

fetch_one() {            # name -> appends a TSV row: name url status type bytes sha etag lastmod
  local name="$1" url="$BASE/$1" hdr status type bytes sha etag lastmod
  hdr="$(mktemp)"
  status="$(curl -fsSL -D "$hdr" -o "$name" -w '%{http_code}' "$url")"
  bytes="$(wc -c < "$name" | tr -d ' ')"
  sha="$(shasum -a 256 "$name" | awk '{print $1}')"
  type="$(awk 'tolower($1)=="content-type:"{$1="";sub(/^ /,"");print;exit}' "$hdr" | tr -d '\r')"
  etag="$(awk 'tolower($1)=="etag:"{print $2;exit}' "$hdr" | tr -d '\r"')"
  lastmod="$(awk 'tolower($1)=="last-modified:"{$1="";sub(/^ /,"");print;exit}' "$hdr" | tr -d '\r')"
  rm -f "$hdr"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$name" "$url" "$status" "${type:-}" "$bytes" "$sha" "${etag:-}" "${lastmod:-}" >> "$TSV"
  printf '  %-24s %s  %sB\n' "$name" "$status" "$bytes"
}

echo "Fetching llms.txt spec from $BASE ..."
for f in "${MD_FILES[@]}"; do fetch_one "$f"; done

# Track the HTML page so we know when llmstxt-js.md needs re-converting.
prev_html_sha="$(shasum -a 256 "$HTML_FILE" 2>/dev/null | awk '{print $1}' || true)"
fetch_one "$HTML_FILE"
new_html_sha="$(shasum -a 256 "$HTML_FILE" | awk '{print $1}')"
if [ -n "$prev_html_sha" ] && [ "$prev_html_sha" != "$new_html_sha" ]; then
  echo "  ⚠ $HTML_FILE changed upstream — re-convert llmstxt-js.md by hand."
fi

# Assemble metadata.json from the collected rows.
FETCHED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)" python3 - "$TSV" "$META" "$BASE" "$HTML_FILE" <<'PY'
import json, os, sys
tsv, meta_path, base, html_file = sys.argv[1:5]
cols = ["file", "url", "http_status", "content_type", "bytes", "sha256", "etag", "last_modified"]
files = []
with open(tsv, encoding="utf-8") as fh:
    for line in fh:
        row = dict(zip(cols, line.rstrip("\n").split("\t"), strict=True))
        row["http_status"] = int(row["http_status"])
        row["bytes"] = int(row["bytes"])
        for k in ("etag", "last_modified", "content_type"):
            row[k] = row[k] or None
        if row["file"] == html_file:
            row["note"] = "HTML-only upstream; converted by hand to llmstxt-js.md"
        files.append(row)
meta = {
    "source": base,
    "fetched_at": os.environ["FETCHED_AT"],
    "fetched_by": "fetch.sh",
    "file_count": len(files),
    "files": sorted(files, key=lambda r: r["file"]),
}
with open(meta_path, "w", encoding="utf-8") as fh:
    json.dump(meta, fh, indent=2)
    fh.write("\n")
print(f"Wrote {meta_path} ({len(files)} files).")
PY
