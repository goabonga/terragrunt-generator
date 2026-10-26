#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

"""Re-author and sign the HEAD commit using only trusted code and Git plumbing.

Run by `git rebase --exec` from ci_automation.py, once per replayed commit.
"""

import re
import subprocess

# The conventional types, plus the `deprecate` and `remove` types that
# multicz.toml layers on top of them.
TYPES = "feat|fix|refactor|test|docs|chore|style|perf|build|ci|revert|deprecate|remove"
SUBJECT = re.compile(rf"(?:{TYPES})(?:\([a-z0-9-]+\))?: [a-z].{{0,70}}")
DROPPED_TRAILER = re.compile(
    r"\s*(?:co-authored-by|signed-off-by|breaking[ _-]change):", re.I
)
DROPPED_FOOTER = re.compile(r"\s*generated (?:with|by)\b", re.I)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def clean_message(text: str) -> str:
    """The commit message without attribution trailers and breaking markers.

    Raises ``SystemExit`` when the subject is not a valid Conventional Commit.
    """
    lines = text.splitlines()
    subject = re.sub(r"^([a-z-]+(?:\([^)]*\))?)!: ", r"\1: ", lines[0])
    if (
        not SUBJECT.fullmatch(subject)
        or len(subject) > 72
        or subject.endswith(".")
    ):
        raise SystemExit("Refusing an invalid Conventional Commit subject")
    body = [
        line
        for line in lines[1:]
        if not DROPPED_TRAILER.match(line) and not DROPPED_FOOTER.match(line)
    ]
    message = subject + "\n"
    if "\n".join(body).strip():
        message += "\n" + "\n".join(body).strip() + "\n"
    return message


def main() -> None:
    message = clean_message(git("log", "-1", "--format=%B").decode())
    signing_key = git("config", "--get", "user.signingkey").decode().strip()
    _ = subprocess.run(
        [
            "git",
            "-c",
            "core.hooksPath=/dev/null",
            "commit",
            "--amend",
            "--reset-author",
            f"--gpg-sign={signing_key}",
            "--file=-",
            "--quiet",
        ],
        input=message.encode(),
        check=True,
    )
    _ = subprocess.run(["git", "verify-commit", "HEAD"], check=True)


if __name__ == "__main__":
    main()
