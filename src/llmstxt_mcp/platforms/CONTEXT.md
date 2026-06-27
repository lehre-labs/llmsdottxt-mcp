# Platforms Context

Documentation platform detection language.

## Language

**Platform Detector**:
A `BasePlatform` subclass that recognizes a documentation Platform from the homepage response body or its URL and builds a `PlatformHint`.
_Avoid_: detector, classifier, recognizer, site matcher

**Platform Registry**:
The priority-ordered list of detectors used by `detect_platform()` to probe the homepage and return the first match, falling back to `default_hint()`.
_Avoid_: detector list, platform table
