#!/usr/bin/env bash

# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

# Rewrite the current HEAD commit with a Conventional Commits prefix
# inferred from the files it touches, then amend with --reset-author
# and a GPG signature so the commit is attributed to and signed by the
# maintainer's identity (configured by the caller workflow).
#
# Routing rules (first-match wins):
#
#   .github/workflows/*.yml   → ci:
#   pyproject.toml / uv.lock  → chore(deps):
#   anything else             → chore(deps):
#
# `chore(deps):` is intentionally non-releasing: routine dependency
# bumps should not cut a release on their own. Re-type a commit to
# `fix:` by hand if a runtime-dependency bump warrants a patch release.
#
# Designed to be invoked by `git rebase --exec` against each commit of
# a Dependabot pull request. Stand-alone use is fine too.

set -euo pipefail

changed=$(git show --name-only --pretty='' HEAD)

case "$changed" in
    *.github/workflows/*)
        prefix="ci"
        ;;
    *pyproject.toml* | *uv.lock*)
        prefix="chore(deps)"
        ;;
    *)
        prefix="chore(deps)"
        ;;
esac

original=$(git log -1 --pretty=%B HEAD)

# Strip any existing Conventional-style prefix from the subject and
# lowercase the leading "Bump" that Dependabot uses by default so the
# rewritten subject reads naturally.
subject=$(printf '%s' "$original" \
    | head -n 1 \
    | sed -E 's/^[a-z-]+(\([^)]+\))?:[[:space:]]*//' \
    | sed 's/^[Bb]ump /bump /')

# Preserve the body but drop any `Co-Authored-By:` trailer Dependabot
# (or anything else) might have added - this repo enforces a strict
# no-co-author policy.
body=$(printf '%s' "$original" \
    | tail -n +2 \
    | sed '/^Co-Authored-By:/d')

if [ -n "$body" ]; then
    new_msg=$(printf '%s: %s\n\n%s' "$prefix" "$subject" "$body")
else
    new_msg=$(printf '%s: %s' "$prefix" "$subject")
fi

git commit --amend --reset-author -m "$new_msg" --quiet
