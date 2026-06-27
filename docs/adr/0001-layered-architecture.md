# Layered architecture enforced by import-linter

The discovery flow (scan → resolve → detect platform → fetch → index) is easy to entangle. We adopted a strict layered import contract (`cli → server → tools/resources/prompts → pipeline → scanners/resolvers/platforms/fetcher/index → http → config/errors → models`) enforced by `import-linter`, with `pipeline` as the single orchestrator.

## Consequences

Adding an ecosystem/platform is a localized change. Upward imports fail CI. Data models live at the bottom so discovery siblings stay independent.
