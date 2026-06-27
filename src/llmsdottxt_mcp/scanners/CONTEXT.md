# Scanners Context

Dependency manifest scanning language.

## Language

**Scanner**:
A `BaseScanner` subclass that detects and parses one manifest type into `Dependency` objects.
_Avoid_: parser, detector, extractor

**Scanner Registry**:
The ordered list of scanners + `detect_ecosystem()` that finds the first scanner whose `can_handle` returns true for the project root.
_Avoid_: scanner list, manifest scanner
