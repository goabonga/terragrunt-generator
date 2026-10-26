#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

"""Re-author and GPG-sign a Dependabot commit as a Conventional Commit.

The type reflects what the bump affects:
  - GitHub Actions bumps      -> ci          (not shipped)
  - dev / docs / tooling bumps -> chore(deps)  (not shipped, no release)
  - runtime dependency bumps   -> fix(deps)    (shipped -> patch release)

Runtime is decided by membership in [project].dependencies of
pyproject.toml; anything else (dependency groups, transitive tooling
dependencies) is not shipped. Run by `git rebase --exec` in dependabot-rewrite.yml.
"""

import re
import subprocess
import tomllib
from pathlib import Path

LEADING_TYPE = re.compile(r"^[a-z]+(\([^)]+\))?!?:\s*")
SINGLE_BUMP = re.compile(r"^[Bb]ump ([A-Za-z0-9._-]+) from ")
TRAILER = re.compile(r"^co-authored-by:", re.I)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def normalize(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def requirement_name(spec: str) -> str:
    return normalize(re.split(r"[\[<>=~!; ]", spec, maxsplit=1)[0])


def is_runtime_dependency(package: str, pyproject: str = "pyproject.toml") -> bool:
    """True if ``package`` is declared in [project].dependencies."""
    data = tomllib.loads(Path(pyproject).read_text())
    runtime = data.get("project", {}).get("dependencies", [])
    return normalize(package) in {requirement_name(d) for d in runtime}


def commit_type(changed: list[str], text: str) -> str:
    if any(".github/workflows/" in path for path in changed):
        return "ci"
    if re.search(r"dev-tools group", text, re.I):
        return "chore(deps)"
    match = SINGLE_BUMP.match(text)
    if match and is_runtime_dependency(match.group(1)):
        return "fix(deps)"
    return "chore(deps)"


def rewrite(changed: list[str], subject: str, body: str) -> str:
    """The Conventional Commit message of a Dependabot commit."""
    text = LEADING_TYPE.sub("", subject)
    body = "\n".join(line for line in body.splitlines() if not TRAILER.match(line)).strip()
    message = f"{commit_type(changed, text)}: {text}"
    return f"{message}\n\n{body}" if body else message


def main() -> None:
    changed = git("show", "--name-only", "--pretty=", "HEAD").splitlines()
    message = rewrite(
        changed, git("log", "-1", "--pretty=%s", "HEAD"), git("log", "-1", "--pretty=%b", "HEAD")
    )
    _ = subprocess.run(
        ["git", "commit", "--amend", "--reset-author", "-m", message, "--quiet"], check=True
    )


if __name__ == "__main__":
    main()
