#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

"""Track each rewritten Dependabot pull request with an issue.

Run from the trusted checkout by dependabot-rewrite.yml:

- ``link`` creates the issue of the pull request (titled like it, labelled
  ``dependencies`` and assigned to the repository owner), or renames the
  existing one, and adds ``Closes #N`` to the pull request description.
- ``close`` closes that issue once the pull request is closed: completed
  when it was merged, not planned when Dependabot or a maintainer dropped it.

The issue is found again through a marker in its body, never through the
pull request description, which Dependabot rewrites when it recreates the
pull request. GitHub closes the issue itself for a merge through the
interface; ``close`` covers the signed merge, a push, and abandoned pull
requests.
"""

import os
import sys

from ci_automation import api, repository

LABEL = "dependencies"


def marker(number: int) -> str:
    return f"<!-- dependabot-pr:{number} -->"


def owner() -> str:
    return repository().split("/")[0]


def find_issue(number: int) -> dict | None:
    pages = api(
        f"repos/{repository()}/issues?state=all&labels={LABEL}&per_page=100",
        paginate=True,
    )
    tag = marker(number)
    for page in pages:
        for issue in page:
            if "pull_request" not in issue and tag in (issue["body"] or ""):
                return issue
    return None


def link(number: int) -> None:
    pull = api(f"repos/{repository()}/pulls/{number}")
    issue = find_issue(number)
    if issue is None:
        issue = api(
            f"repos/{repository()}/issues",
            "POST",
            {
                "title": pull["title"],
                "body": f"Tracks pull request #{number}.\n\n{marker(number)}",
                "labels": [LABEL],
                "assignees": [owner()],
            },
        )
    elif issue["title"] != pull["title"]:
        api(
            f"repos/{repository()}/issues/{issue['number']}",
            "PATCH",
            {"title": pull["title"]},
        )
    closing = f"Closes #{issue['number']}"
    body = pull["body"] or ""
    if closing not in body:
        api(
            f"repos/{repository()}/pulls/{number}",
            "PATCH",
            {"body": f"{body}\n\n{closing}".strip()},
        )


def close(number: int, merged: bool) -> None:
    issue = find_issue(number)
    if issue is None or issue["state"] == "closed":
        return
    api(
        f"repos/{repository()}/issues/{issue['number']}",
        "PATCH",
        {"state": "closed", "state_reason": "completed" if merged else "not_planned"},
    )


if __name__ == "__main__":
    pr = int(os.environ["PR_NUMBER"])
    if sys.argv[1:2] == ["link"]:
        link(pr)
    elif sys.argv[1:2] == ["close"]:
        close(pr, os.environ.get("MERGED") == "true")
    else:
        sys.exit("usage: dependabot_issue.py link | close")
