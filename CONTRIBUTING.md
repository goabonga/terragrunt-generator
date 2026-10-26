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

# Second type checker, in standard mode (pyright on src/).
uv run pyright
```

These checks run in CI and gate the release, along with the tests, the
SPDX header check and the security scans. Each CI job writes a summary of
its result on the run page.

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

1. Fork the repository and create a topic branch from `main`, or from the
   branch of the issue you work on (see [Branch names](#branch-names)).
2. Keep commits small, focused and atomic.
3. Open a pull request against `main`, or against the issue branch for a
   sub-issue. The CI workflow runs the full quality matrix (lint,
   type-check, tests, security scans) on both.
4. Reviews target correctness, scope and adherence to the
   conventional-commits contract; please do not bundle unrelated changes.

### Branch names

A branch is named after the GitHub issue it addresses:

```
issue-<number>-<slug>
```

`<number>` is the issue number and `<slug>` a few lowercase words separated
by hyphens, for example `issue-12-code-readability`. Keep it free of `/`:
Git cannot hold `issue-12` and `issue-12/...` at the same time, and the
automation only recognises `issue-*` as a base branch.

| Work | Branch | Created from | Pull request into |
| --- | --- | --- | --- |
| An issue | `issue-<number>-<slug>` | `main` | `main` |
| A sub-issue of an issue | `issue-<number>-<slug>` (its own issue number) | the branch of the parent issue | the branch of the parent issue |

An issue split into sub-issues therefore gets one branch of its own, which
collects the pull requests of its sub-issues. Once they are all merged, the
issue branch is proposed to `main` in a single pull request. Dependabot
branches (`dependabot/...`) are created by Dependabot and need no naming.

### Merging

Adding the `auto-merge` label to a pull request, by someone with write
access, replays its commits GPG-signed onto its base branch once the
required checks passed, then fast-forwards that branch: `main`, or the issue
branch for a sub-issue. The history stays linear. The commits of a branch
pushed unsigned, such as by GitHub's "Update branch", are re-signed in place.

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
to PyPI. The documentation site is redeployed only when the `docs`
component is bumped, by a `docs:` commit or by a package release. The
`chore(release)` commit pushed back by multicz does not start another run.
Maintainers do not need to bump versions, edit changelogs or create tags by
hand.

## Reporting bugs and asking for features

Please open a GitHub issue. For security-sensitive reports, follow
[SECURITY.md](SECURITY.md) instead of the public tracker.
