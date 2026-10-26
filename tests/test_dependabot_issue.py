# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import importlib.util
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

SCRIPTS = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location(
    "dependabot_issue", SCRIPTS / "dependabot_issue.py"
)
assert spec is not None and spec.loader is not None
tracker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracker)

REPO = "owner/demo"
TITLE = "fix(deps): bump requests from 1 to 2"


@pytest.fixture(autouse=True)
def env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GH_REPO", REPO)
    monkeypatch.setenv("PR_NUMBER", "13")


def issue(
    number: int = 40, pr: int = 13, state: str = "open", title: str = TITLE
) -> dict[str, Any]:
    return {
        "number": number,
        "state": state,
        "title": title,
        "body": f"Tracks pull request #{pr}.\n\n{tracker.marker(pr)}",
    }


class Api:
    """A GitHub stub: the pull request, the issues of the repository, the writes."""

    def __init__(
        self, issues: list[dict[str, Any]], body: str | None = "Release notes"
    ) -> None:
        self.issues = issues
        self.pull = {"title": TITLE, "body": body}
        self.writes: list[tuple[str, str, Any]] = []

    def __call__(
        self,
        endpoint: str,
        method: str = "GET",
        payload: Any = None,
        paginate: bool = False,
    ) -> Any:
        if method != "GET":
            self.writes.append((method, endpoint, payload))
            return {"number": 41, "title": TITLE, "body": ""}
        if endpoint.endswith("/pulls/13"):
            return self.pull
        assert paginate
        return [self.issues]


def run(stub: Api, action: str, *args: Any) -> None:
    with patch.object(tracker, "api", stub):
        getattr(tracker, action)(13, *args)


def test_the_issue_is_found_through_its_marker() -> None:
    other = issue(number=39, pr=12)
    stub = Api([other, {**issue(number=38), "pull_request": {}}, issue()])
    with patch.object(tracker, "api", stub):
        assert tracker.find_issue(13) == issue()
        assert tracker.find_issue(99) is None


def test_link_creates_the_issue_and_closes_it_from_the_pull_request() -> None:
    stub = Api([])
    run(stub, "link")
    assert stub.writes == [
        (
            "POST",
            f"repos/{REPO}/issues",
            {
                "title": TITLE,
                "body": f"Tracks pull request #13.\n\n{tracker.marker(13)}",
                "labels": ["dependencies"],
                "assignees": ["owner"],
            },
        ),
        ("PATCH", f"repos/{REPO}/pulls/13", {"body": "Release notes\n\nCloses #41"}),
    ]


def test_link_without_a_description_only_holds_the_keyword() -> None:
    stub = Api([], body=None)
    run(stub, "link")
    assert stub.writes[-1][2] == {"body": "Closes #41"}


def test_link_is_idempotent() -> None:
    stub = Api([issue()], body="Release notes\n\nCloses #40")
    run(stub, "link")
    assert stub.writes == []


def test_link_restores_the_keyword_after_dependabot_rewrote_the_description() -> None:
    stub = Api([issue()])
    run(stub, "link")
    assert stub.writes == [
        ("PATCH", f"repos/{REPO}/pulls/13", {"body": "Release notes\n\nCloses #40"})
    ]


def test_link_renames_the_issue_after_the_pull_request() -> None:
    stub = Api(
        [issue(title="chore(deps): bump requests from 1 to 2")], body="Closes #40"
    )
    run(stub, "link")
    assert stub.writes == [("PATCH", f"repos/{REPO}/issues/40", {"title": TITLE})]


@pytest.mark.parametrize(
    ("merged", "reason"), [(True, "completed"), (False, "not_planned")]
)
def test_close_gives_the_reason_of_the_pull_request(merged: bool, reason: str) -> None:
    stub = Api([issue()])
    run(stub, "close", merged)
    assert stub.writes == [
        (
            "PATCH",
            f"repos/{REPO}/issues/40",
            {"state": "closed", "state_reason": reason},
        )
    ]


@pytest.mark.parametrize("issues", [[], [issue(state="closed")]])
def test_close_leaves_a_missing_or_closed_issue_alone(
    issues: list[dict[str, Any]],
) -> None:
    stub = Api(issues)
    run(stub, "close", True)
    assert stub.writes == []
