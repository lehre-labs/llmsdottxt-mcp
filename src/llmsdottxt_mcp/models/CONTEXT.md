# Models Context

Typed shapes used across the server -- domain, persisted, and response models.

## Language

**Scan Report**:
Tool response summarizing a scan run: packages scanned, resolved, failed, timing.
_Avoid_: scan result, scan output, completion report

**Package Summary**:
A read-only projection of one Index Entry for list/search operations.
_Avoid_: package card, brief, entry summary

**Search Hit**:
A ranked match from full-text search: score, excerpt, and source file path.
_Avoid_: result, match, find

**Browse TOC**:
Tool response for ``browse(package)``: package metadata plus the full section tree with links.
_Avoid_: browse result, toc response, section view

**Status Report**:
Tool response exposing index size, freshness, and cache directory path.
_Avoid_: health check, diagnostics, server info

**Index Meta**:
The `index_meta` table tracking how many packages were last indexed and when.
_Avoid_: index state, summary, index manifest

**Section**:
An H2-H6 heading group of links; ``level`` tracks the heading depth (2-6).
_Avoid_: heading group, link group
