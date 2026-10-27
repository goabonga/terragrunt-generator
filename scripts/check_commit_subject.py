#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

"""Check that commit subjects are valid Conventional Commits.

The signed merge replays every commit through sign_commit.py, which refuses
a subject that is not a Conventional Commit, is longer than 72 characters or
ends with a period. This applies the same rule earlier, where it is cheap to
fix: as the commit-msg hook (``check_commit_subject.py MESSAGE_FILE``) and in
CI on the commits of a pull request (``check_commit_subject.py --range
BASE..HEAD``). The hook lets autosquash commits (``fixup!``) through.
"""

import re
import subprocess
import sys

from sign_commit import SUBJECT

LIMIT = 72
# `git commit --fixup` and `--squash` subjects are meant to be squashed away
# before the pull request: only the commits CI looks at must be valid.
AUTOSQUASH = ("fixup! ", "squash! ", "amend! ")


def problem(subject: str) -> str | None:
    """Why ``subject`` is refused, or None when it is valid."""
    subject = re.sub(r"^([a-z-]+(?:\([^)]*\))?)!: ", r"\1: ", subject)
    if len(subject) > LIMIT:
        return f"{len(subject)} characters, the limit is {LIMIT}"
    if subject.endswith("."):
        return "ends with a period"
    if not SUBJECT.fullmatch(subject):
        return "not `<type>(<scope>): <lowercase imperative summary>` with a known type"
    return None


def message_subject(path: str) -> str:
    """The subject of a commit message file: its first line that is not a comment."""
    with open(path, encoding="utf-8") as stream:
        lines = [line.rstrip("\n") for line in stream if not line.startswith("#")]
    return next((line for line in lines if line.strip()), "")


def range_subjects(commit_range: str) -> list[tuple[str, str]]:
    log = subprocess.check_output(
        ["git", "log", "--no-merges", "--format=%h %s", commit_range], text=True
    )
    pairs = (line.split(" ", 1) for line in log.splitlines())
    return [(sha, subject) for sha, subject in pairs]


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "--range":
        subjects = range_subjects(argv[1])
    elif len(argv) == 1 and not argv[0].startswith("-"):
        subject = message_subject(argv[0])
        subjects = [] if subject.startswith(AUTOSQUASH) else [("", subject)]
    else:
        print("usage: check_commit_subject.py MESSAGE_FILE | --range BASE..HEAD")
        return 2
    failed = False
    for sha, subject in subjects:
        reason = problem(subject)
        if reason:
            failed = True
            print(f"{sha} {subject!r}: {reason}".strip())
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
