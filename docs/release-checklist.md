# Release Checklist

Use this before tagging a public release.

## Repository Settings

- Enable GitHub private vulnerability reporting.
- Create the `pypi` GitHub environment for PyPI Trusted Publishing.
- Protect release tags matching `v*` and keep branch protection on `main`.

## Local Verification

```sh
uv run ruff format --check
uv run ruff check
uv run ty check
uv run basedpyright
uv run lint-imports
uv run deptry .
uv run bandit -q -c pyproject.toml -r src
uv run pip-audit
uv run pytest -n auto
uv build
```

## Release Verification

- Confirm `pyproject.toml` version and `CHANGELOG.md` describe the release.
- Confirm examples and docs contain no fetched third-party content, private URLs, or tokens.
- Tag with `vMAJOR.MINOR.PATCH`.
- Confirm GitHub Actions published via PyPI Trusted Publishing.
- Confirm release artifacts have GitHub artifact attestations.
