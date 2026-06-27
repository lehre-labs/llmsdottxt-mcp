# python
- Use Python 3.14 (latest stable). Confidence: 0.70
- Avoid using `Any`; use typed Pydantic models with concrete types instead. Confidence: 0.70
- Use `Literal` type for constrained string values (e.g., log level). Confidence: 0.70

# architecture
- Use the registry pattern for extensible components (resolvers/, platforms/, scanners/). Confidence: 0.70

# documentation
- Create AGENTS.md + CONTEXT.md paired files for each module. Confidence: 0.70

# configuration
- CLAUDE.md should reference '@AGENTS.md' to point to the project knowledge system. Confidence: 0.70

# project
- Use lehre-labs GitHub organization for project URLs and metadata. Confidence: 0.70
