#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

"""Split a grouped Dependabot lock update into one commit per dependency.

A group bumps several dependencies in a single commit that only touches
uv.lock, so one type (and one release decision) covers all of them. Each
dependency declared in pyproject.toml gets its own commit instead:
``fix(deps)`` when it ships (runtime), ``chore(deps)`` otherwise.

Two commands, run by dependabot-rewrite.yml from the trusted checkout:

- ``prepare BASE OUT`` regenerates the lock one dependency at a time with
  ``uv lock --upgrade-package`` and stores each state in OUT. It prints the
  number of commits to make, or 0 when the update must stay a single
  commit: the head changes more than uv.lock, fewer than two declared
  dependencies moved, uv failed, or the regenerated lock differs from the
  one Dependabot proposed. It runs before the signing key is imported.
- ``commit OUT`` replays the stored states on BASE, one commit each, with
  the git identity and signing configured by the workflow.

Runtime dependencies come first so the pull request title, which follows
the first commit, carries the type that triggers a release.
"""

import subprocess
import sys
import tomllib
from pathlib import Path

from rewrite_dependabot_commit import (
    git,
    is_runtime_dependency,
    normalize,
    requirement_name,
)

LOCK = "uv.lock"
PYPROJECT = "pyproject.toml"


def blob(revision: str, path: str) -> str:
    return subprocess.check_output(["git", "show", f"{revision}:{path}"], text=True)


def locked_versions(text: str) -> dict[str, list[str]]:
    versions: dict[str, list[str]] = {}
    for package in tomllib.loads(text).get("package", []):
        versions.setdefault(normalize(package["name"]), []).append(
            package.get("version", "")
        )
    return {name: sorted(found) for name, found in versions.items()}


def declared_packages(pyproject: str = PYPROJECT) -> set[str]:
    """Every dependency named in [project] or in a dependency group."""
    data = tomllib.loads(Path(pyproject).read_text())
    project = data.get("project", {})
    specs = list(project.get("dependencies", []))
    for extra in project.get("optional-dependencies", {}).values():
        specs.extend(extra)
    for group in data.get("dependency-groups", {}).values():
        specs.extend(entry for entry in group if isinstance(entry, str))
    return {requirement_name(spec) for spec in specs}


def updates(
    base_lock: str, head_lock: str, declared: set[str]
) -> list[tuple[str, str, str]]:
    """The declared dependencies whose locked version moved, as (name, old, new)."""
    old, new = locked_versions(base_lock), locked_versions(head_lock)
    moved: list[tuple[str, str, str]] = []
    for name in sorted(declared & old.keys() & new.keys()):
        if old[name] == new[name]:
            continue
        if len(old[name]) != 1 or len(new[name]) != 1:
            return []
        moved.append((name, old[name][0], new[name][0]))
    return moved


def runtime_first(moved: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    return sorted(
        moved, key=lambda entry: (not is_runtime_dependency(entry[0]), entry[0])
    )


def subject(name: str, old: str, new: str) -> str:
    kind = "fix" if is_runtime_dependency(name) else "chore"
    return f"{kind}(deps): bump {name} from {old} to {new}"


def upgrade(name: str, version: str) -> None:
    _ = subprocess.run(
        ["uv", "lock", "--upgrade-package", f"{name}=={version}"],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def prepare(base: str, out: str) -> int:
    if git("diff", "--name-only", base, "HEAD").splitlines() != [LOCK]:
        return 0
    base_lock, head_lock = blob(base, LOCK), Path(LOCK).read_text()
    moved = runtime_first(updates(base_lock, head_lock, declared_packages()))
    if len(moved) < 2:
        return 0
    target = Path(out)
    target.mkdir(parents=True, exist_ok=True)
    regenerated = ""
    try:
        Path(LOCK).write_text(base_lock)
        for index, (name, old, new) in enumerate(moved, 1):
            upgrade(name, new)
            regenerated = Path(LOCK).read_text()
            _ = (target / f"{index:02}.lock").write_text(regenerated)
            _ = (target / f"{index:02}.msg").write_text(subject(name, old, new))
    except (OSError, subprocess.CalledProcessError):
        return 0
    finally:
        _ = git("checkout", "HEAD", "--", LOCK)
    if tomllib.loads(regenerated) != tomllib.loads(head_lock):
        return 0
    _ = (target / "base").write_text(base)
    return len(moved)


def commit(out: str) -> None:
    source = Path(out)
    _ = git("reset", "--hard", (source / "base").read_text())
    for lock in sorted(source.glob("*.lock")):
        _ = Path(LOCK).write_text(lock.read_text())
        _ = git("add", LOCK)
        message = lock.with_suffix(".msg").read_text()
        _ = subprocess.run(["git", "commit", "-m", message, "--quiet"], check=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["prepare"]:
        print(prepare(sys.argv[2], sys.argv[3]))
    elif sys.argv[1:2] == ["commit"]:
        commit(sys.argv[2])
    else:
        sys.exit("usage: split_dependabot_lock.py prepare BASE OUT | commit OUT")
