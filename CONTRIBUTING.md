# Contributing to terragrunt-generator

Thanks for taking the time to contribute. This document is the short version
of how to propose a change and what the project expects in return.

## Code of Conduct

Participation in this project is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md). By contributing you agree to abide by
its terms.

## Development setup

```bash
# Clone and sync the project (Python 3.13+).
git clone https://github.com/goabonga/terragrunt-generator.git
cd terragrunt-generator
uv sync

# Install the pre-commit and commit-msg hooks (runs ruff check/format,
# mypy strict, SPDX header checks, and Conventional Commits validation
# before each commit lands).
uv run pre-commit install
```

To run all hooks manually on every tracked file:

```bash
uv run pre-commit run --all-files
```

## Running the tests

```bash
# Full suite with coverage.
uv run pytest --cov=terragrunt_generator
```

## Lint and type checks

```bash
# Lint (ruff: E, F, I, B, UP, SIM).
uv run ruff check src tests

# Format check.
uv run ruff format --check src tests

# Strict static type checking (mypy on src/).
uv run mypy src
```

All three checks run in CI and gate the release.

## License headers

Every Python, YAML and TOML file in the repository must start with the
two-line SPDX header below (after the shebang, if any):

```
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>
```

A helper script applies and verifies the headers:

```bash
# Add missing headers in-place.
python scripts/add_license_header.py --path . --types py,yml,toml

# Fail with non-zero exit if any tracked file is missing the header.
python scripts/add_license_header.py --path . --types py,yml,toml --check
```

Markdown, `LICENSE`, `uv.lock`, `.gitignore` and `py.typed` markers are
intentionally excluded.

## Branching and pull requests

1. Fork the repository and create a topic branch from `main`.
2. Keep commits small, focused and atomic.
3. Open a pull request against `main`. The CI workflow runs the full
   quality matrix (lint, type-check, tests, security scans).
4. Reviews target correctness, scope and adherence to the
   conventional-commits contract; please do not bundle unrelated changes.

## Commit messages

Commit messages MUST follow
[Conventional Commits](https://www.conventionalcommits.org/). They drive the
version bumps and changelog computed by
[multicz](https://github.com/goabonga/multicz).

| Type | Effect on version | Use it for |
| --- | --- | --- |
| `feat` | minor | new user-facing capability |
| `fix` | patch | bug fix |
| `perf` | patch | performance improvement |
| `deprecate` | minor | announce an upcoming removal (raises a `DeprecationWarning`); routed to `### Deprecated` in `CHANGELOG.md` |
| `remove` | minor | perform the removal after the n+2 window completes; routed to `### Removed` in `CHANGELOG.md` |
| `refactor`, `docs`, `test`, `chore`, `ci`, `build`, `style` | none | maintenance, no release |
| `feat!` / `BREAKING CHANGE:` | major | incompatible change bypassing the deprecation cycle (security, design errors that cannot wait) |

Examples:

```
feat(cli): support multiple --yaml-output options
fix(generate): preserve quoted defaults in inputs block
docs: clarify the --lookup syntax
```

Do not append `Co-Authored-By` trailers; the workflow expects a single
authored release commit per push.

## Deprecations

Any commit that deprecates or removes a public symbol MUST follow the
[stability and deprecation policy](docs/stability.md):
announce with a `DeprecationWarning` in version `n + 1`, remove in
`n + 2`. Removal commits are regular `feat:` (no `!`) - under the n+2
contract, a removal after the warning window is not a breaking change
and lands in a minor release. Reserve `feat!:` / `BREAKING CHANGE:`
for changes that bypass the deprecation cycle.

## Releasing

Releases are fully automated. On every push to `main`, the workflow runs
`multicz bump --commit --tag --push` and then publishes the bumped package
to PyPI. Maintainers do not need to bump versions, edit changelogs or create
tags by hand.

## Reporting bugs and asking for features

Please open a GitHub issue. For security-sensitive reports, follow
[SECURITY.md](SECURITY.md) instead of the public tracker.
