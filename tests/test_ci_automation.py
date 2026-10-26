# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

"""The trusted automation behind resign, auto-merge and Dependabot queueing."""

import importlib.util
import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

SCRIPTS = Path(__file__).parent.parent / "scripts"


def load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ci = load("ci_automation")
sign = load("sign_commit")

SHA = "a" * 40
REPO = "owner/demo"


def pull(
    sha: str = SHA,
    repo: str = REPO,
    base: str = "main",
    ref: str = "feature/x",
    number: int = 9,
    labels: tuple[str, ...] = (),
    user: str = "someone",
    draft: bool = False,
    body: str = "",
) -> dict[str, Any]:
    return {
        "number": number,
        "state": "open",
        "draft": draft,
        "body": body,
        "user": {"login": user},
        "labels": [{"name": name} for name in labels],
        "head": {"sha": sha, "ref": ref, "repo": {"full_name": repo}},
        "base": {"ref": base},
    }


def commit(verified: bool, message: str = "chore: x") -> dict[str, Any]:
    return {
        "sha": ("b" if verified else "c") * 40,
        "commit": {"verification": {"verified": verified}, "message": message},
    }


@pytest.fixture(autouse=True)
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    output = tmp_path / "output"
    values = {
        "GH_REPO": REPO,
        "PR": "9",
        "HEAD_SHA": SHA,
        "HEAD_REF": "feature/x",
        "SIGNAL_SHA": SHA,
        "SIGNAL_BRANCH": "feature/x",
        "LABELLER": "goabonga",
        "MERGE_LABEL": "auto-merge",
        "PR_WRITE_TOKEN": "token",
        "RUNNER_TEMP": str(tmp_path),
        "GITHUB_OUTPUT": str(output),
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return output


def outputs(path: Path) -> dict[str, str]:
    return dict(line.split("=", 1) for line in path.read_text().splitlines())


def paged(items: list[Any]) -> list[list[Any]]:
    return [items]


def resign(
    pulls: list[Any], commits: list[Any], permission: str = "admin"
) -> list[str]:
    calls: list[str] = []

    def respond(endpoint: str, *args: Any, **kwargs: Any) -> Any:
        calls.append(endpoint)
        if "/collaborators/" in endpoint:
            return {"permission": permission}
        if endpoint.endswith("/commits?per_page=100"):
            return paged(commits)
        return paged(pulls)

    with patch.object(ci, "api", side_effect=respond):
        ci.validate_resign()
    return calls


def test_unsigned_commits_pushed_by_a_writer_are_re_signed(env: Path) -> None:
    calls = resign([pull()], [commit(True), commit(False)])
    assert outputs(env) == {"number": "9", "needed": "true"}
    assert any("/collaborators/goabonga/permission" in call for call in calls)


def test_a_fully_signed_branch_needs_nothing_and_cannot_loop(env: Path) -> None:
    calls = resign([pull()], [commit(True), commit(True)])
    assert outputs(env) == {"number": "9", "needed": "false"}
    assert not any("/collaborators/" in call for call in calls)


@pytest.mark.parametrize(
    "pulls",
    [
        [pull(sha="d" * 40)],
        [pull(repo="fork/demo")],
        [pull(base="develop")],
        [pull(ref="main")],
        [],
    ],
)
def test_stale_forked_or_other_base_pull_requests_are_left_alone(
    env: Path, pulls: list[Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    if pulls and pulls[0]["head"]["ref"] == "main":
        monkeypatch.setenv("SIGNAL_BRANCH", "main")
    resign(pulls, [commit(False)])
    assert outputs(env)["needed"] == "false"


def test_a_pusher_without_write_access_is_refused() -> None:
    with pytest.raises(ValueError, match="write access"):
        resign([pull()], [commit(False)], permission="read")


def test_re_signing_keeps_the_branch_base_and_order() -> None:
    calls = []

    def fake_git(*args: str) -> str:
        calls.append(args)
        return "e" * 40 if args[0] == "merge-base" else ""

    with (
        patch.object(ci, "git", side_effect=fake_git),
        patch.object(ci.subprocess, "run") as run,
    ):
        ci.rebase("resign")
    assert ("merge-base", "origin/main", "HEAD") in calls
    assert not any(args[:1] == ("fetch",) for args in calls)
    command = run.call_args.args[0]
    assert command[:5] == ["git", "rebase", "--force-rebase", "--empty=keep", "e" * 40]
    assert "sign_commit.py" in command[-1]


def test_merging_replays_onto_the_latest_main(tmp_path: Path) -> None:
    calls = []

    def fake_git(*args: str) -> str:
        calls.append(args)
        return "f" * 40 if args[0] == "rev-parse" else ""

    with (
        patch.object(ci, "git", side_effect=fake_git),
        patch.object(ci.subprocess, "run") as run,
    ):
        ci.rebase("merge")
    assert ("fetch", "origin", "main") in calls
    assert (tmp_path / "merge-base-sha").read_text() == "f" * 40
    assert run.call_args.args[0][4] == "f" * 40


def test_merge_commits_cannot_be_replayed() -> None:
    def fake_git(*args: str) -> str:
        return "m" * 40 if args[0] == "rev-list" else "e" * 40

    with (
        patch.object(ci, "git", side_effect=fake_git),
        pytest.raises(ValueError, match="Merge commits"),
    ):
        ci.rebase("resign")


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({}, False),
        ({"labels": ("auto-merge",)}, True),
        ({"labels": ("auto-merge",), "draft": True}, False),
        ({"labels": ("auto-merge",), "sha": "d" * 40}, False),
        ({"labels": ("auto-merge",), "repo": "fork/demo"}, False),
        ({"labels": ("auto-merge",), "base": "develop"}, False),
        ({"labels": ("auto-merge",), "ref": "other"}, False),
    ],
)
def test_merge_authorization(changes: dict[str, Any], expected: bool) -> None:
    assert ci.merge_authorized(pull(**changes), SHA) is expected


def test_main_itself_is_never_merged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEAD_REF", "main")
    assert not ci.merge_authorized(pull(ref="main", labels=("auto-merge",)), SHA)


def test_validate_merge_needs_the_token_and_the_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GH_TOKEN", "t")
    monkeypatch.delenv("GPG_PRIVATE_KEY", raising=False)
    with (
        patch.object(ci.subprocess, "run"),
        pytest.raises(ValueError, match="signing key"),
    ):
        ci.validate_merge()


def test_validate_merge_refuses_a_removed_label(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GH_TOKEN", "t")
    monkeypatch.setenv("GPG_PRIVATE_KEY", "k")
    with (
        patch.object(ci.subprocess, "run"),
        patch.object(ci, "api", return_value=pull()),
        pytest.raises(ValueError, match="authorization was removed"),
    ):
        ci.validate_merge()


def test_validate_merge_accepts_a_labelled_pull_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GH_TOKEN", "t")
    monkeypatch.setenv("GPG_PRIVATE_KEY", "k")

    def respond(endpoint: str, *args: Any, **kwargs: Any) -> Any:
        if "/collaborators/" in endpoint:
            return {"permission": "write"}
        return pull(labels=("auto-merge",))

    with (
        patch.object(ci.subprocess, "run"),
        patch.object(ci, "api", side_effect=respond),
    ):
        ci.validate_merge()


def run_check(name: str, conclusion: str | None, id: int = 1) -> dict[str, Any]:
    return {
        "id": id,
        "name": name,
        "app": {"id": 1},
        "status": "completed" if conclusion else "in_progress",
        "conclusion": conclusion,
    }


NO_STATUS: dict[str, Any] = {"state": "pending", "statuses": []}


def test_checks_are_ready_once_every_required_check_succeeded() -> None:
    runs = [run_check("lint", "success"), run_check("test", "success", 2)]
    assert ci.checks_ready(runs, NO_STATUS, {"lint", "test"})


def test_a_missing_or_pending_required_check_is_not_ready() -> None:
    assert not ci.checks_ready(
        [run_check("lint", "success")], NO_STATUS, {"lint", "test"}
    )
    pending = [run_check("lint", "success"), run_check("test", None, 2)]
    assert not ci.checks_ready(pending, NO_STATUS, {"lint", "test"})


def test_a_failed_check_aborts() -> None:
    with pytest.raises(ValueError, match="A check failed"):
        ci.checks_ready([run_check("lint", "failure")], NO_STATUS, {"lint"})


def test_a_rerun_supersedes_the_failed_attempt() -> None:
    runs = [run_check("lint", "failure", 1), run_check("lint", "success", 2)]
    assert ci.checks_ready(runs, NO_STATUS, {"lint"})


def test_skipped_required_checks_alone_cannot_merge() -> None:
    assert not ci.checks_ready([run_check("lint", "skipped")], NO_STATUS, {"lint"})


def test_the_merge_job_is_not_waited_for() -> None:
    runs = [run_check("lint", "success"), run_check("merge into main", None, 2)]
    assert ci.checks_ready(runs, NO_STATUS, {"lint"})


def test_without_a_required_check_nothing_is_ready() -> None:
    assert not ci.checks_ready([run_check("lint", "success")], NO_STATUS, set())


def test_a_failed_commit_status_aborts() -> None:
    status = {"state": "failure", "statuses": [{}]}
    with pytest.raises(ValueError, match="commit status"):
        ci.checks_ready([run_check("lint", "success")], status, {"lint"})


def test_required_checks_come_from_the_active_rulesets() -> None:
    rules = [
        {"type": "required_signatures"},
        {
            "type": "required_status_checks",
            "parameters": {
                "required_status_checks": [{"context": "lint"}, {"context": "test"}]
            },
        },
    ]
    with patch.object(ci, "api", return_value=rules) as client:
        assert ci.required_checks() == {"lint", "test"}
    assert client.call_args.args[0] == f"repos/{REPO}/rules/branches/main"


def labelled(number: int, *stamps: str) -> list[Any]:
    return [
        {"event": "labeled", "created_at": s, "label": {"name": "auto-merge"}}
        for s in stamps
    ]


def test_the_queue_is_ordered_by_the_latest_label() -> None:
    events = {1: labelled(1, "2026-01-01", "2026-01-05"), 2: labelled(2, "2026-01-03")}

    def respond(endpoint: str, *args: Any, **kwargs: Any) -> Any:
        if "/events" in endpoint:
            return paged(events[int(endpoint.split("/issues/")[1].split("/")[0])])
        return paged(
            [
                {"number": 1, "pull_request": {}},
                {"number": 2, "pull_request": {}},
                {"number": 3},
            ]
        )

    with patch.object(ci, "api", side_effect=respond):
        assert ci.queue_ahead(1) == [2]
        assert ci.queue_ahead(2) == []


def test_a_pull_request_outside_the_queue_waits_for_all() -> None:
    def respond(endpoint: str, *args: Any, **kwargs: Any) -> Any:
        if "/events" in endpoint:
            return paged(labelled(2, "2026-01-03"))
        return paged([{"number": 2, "pull_request": {}}])

    with patch.object(ci, "api", side_effect=respond):
        assert ci.queue_ahead(7) == [2]


def test_the_queue_waits_while_a_release_is_pending(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUEUE_DIR", str(tmp_path))
    pending = iter([["terragrunt-generator"], []])
    with (
        patch.object(ci, "pull_request", return_value=pull(labels=("auto-merge",))),
        patch.object(ci, "queue_ahead", return_value=[]),
        patch.object(ci, "pending_release", side_effect=lambda _: next(pending)),
        patch.object(ci.time, "sleep") as sleep,
    ):
        ci.wait_turn()
    assert sleep.call_count == 1


def test_the_queue_waits_behind_earlier_pull_requests(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUEUE_DIR", str(tmp_path))
    ahead = iter([[4], []])
    with (
        patch.object(ci, "pull_request", return_value=pull(labels=("auto-merge",))),
        patch.object(ci, "queue_ahead", side_effect=lambda _: next(ahead)),
        patch.object(ci, "pending_release", return_value=[]),
        patch.object(ci.time, "sleep") as sleep,
    ):
        ci.wait_turn()
    assert sleep.call_count == 1


def test_merging_refuses_when_main_advanced(tmp_path: Path) -> None:
    (tmp_path / "merge-base-sha").write_text("1" * 40)

    def fake_git(*args: str) -> str:
        return "2" * 40 if args[:1] == ("rev-parse",) and args[1] != "HEAD" else SHA

    with (
        patch.object(ci, "git", side_effect=fake_git),
        patch.object(ci, "pull_request", return_value=pull(labels=("auto-merge",))),
        patch.object(ci, "check_labeller"),
        pytest.raises(ValueError, match="advanced"),
    ):
        ci.merge()


def test_merging_fast_forwards_main_and_comments(tmp_path: Path) -> None:
    (tmp_path / "merge-base-sha").write_text("1" * 40)

    def fake_git(*args: str) -> str:
        return "1" * 40 if args[1] == "origin/main" else SHA

    with (
        patch.object(ci, "git", side_effect=fake_git),
        patch.object(ci, "pull_request", return_value=pull(labels=("auto-merge",))),
        patch.object(ci, "check_labeller"),
        patch.object(ci, "authenticated_git") as push,
        patch.object(ci, "api") as client,
    ):
        ci.merge()
    push.assert_called_once_with("push", "origin", "HEAD:refs/heads/main")
    assert "Merged into `main`" in client.call_args.args[2]["body"]
    assert client.call_args.kwargs["token"] == "token"


def test_pushing_a_merge_leases_the_validated_head() -> None:
    with (
        patch.object(ci, "git", return_value="abc1234"),
        patch.object(ci.subprocess, "run"),
        patch.object(ci, "pull_request", return_value=pull(labels=("auto-merge",))),
        patch.object(ci, "check_labeller"),
        patch.object(ci, "authenticated_git") as push,
        patch.object(ci, "api") as client,
    ):
        ci.push_signed("merge")
    assert push.call_args.args[1] == f"--force-with-lease=refs/heads/feature/x:{SHA}"
    client.assert_not_called()


def test_pushing_a_merge_refuses_a_stale_pull_request() -> None:
    with (
        patch.object(ci.subprocess, "run"),
        patch.object(ci, "pull_request", return_value=pull(sha="d" * 40)),
        patch.object(ci, "authenticated_git") as push,
        pytest.raises(ValueError, match="authorization was removed"),
    ):
        ci.push_signed("merge")
    push.assert_not_called()


def test_pushing_a_resign_comments_on_the_pull_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EXPECTED_SHA", SHA)
    with (
        patch.object(ci, "git", return_value="abc1234"),
        patch.object(ci.subprocess, "run"),
        patch.object(ci, "pull_request", return_value=pull()),
        patch.object(ci, "check_labeller"),
        patch.object(ci, "authenticated_git") as push,
        patch.object(ci, "api") as client,
    ):
        ci.push_signed("resign")
    push.assert_called_once()
    assert "Re-signed the commits" in client.call_args.args[2]["body"]


def test_pushing_a_resign_refuses_a_moved_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EXPECTED_SHA", SHA)
    with (
        patch.object(ci.subprocess, "run"),
        patch.object(ci, "pull_request", return_value=pull(sha="d" * 40)),
        pytest.raises(ValueError, match="changed while"),
    ):
        ci.push_signed("resign")


@pytest.mark.parametrize(
    ("text", "majors"),
    [
        ("Bumps [requests](https://x) from 2.31.0 to 3.0.0.", ["requests"]),
        ("Bumps [requests](https://x) from 2.31.0 to 2.32.0.", []),
        (
            "Updates `ruff` from 0.13.0 to 1.0.0\nUpdates `mypy` from 1.1 to 1.2",
            ["ruff"],
        ),
        ("nothing announced", []),
    ],
)
def test_major_updates(text: str, majors: list[str]) -> None:
    assert ci.major_updates(text) == majors


def dependabot(**changes: Any) -> dict[str, Any]:
    return pull(
        ref="dependabot/uv/requests-2",
        user="dependabot[bot]",
        number=5,
        **changes,
    )


def label_run(
    pr: dict[str, Any], commits: list[Any], comments: list[Any] | None = None
) -> Any:
    def respond(endpoint: str, *args: Any, **kwargs: Any) -> Any:
        if endpoint.endswith("/comments?per_page=100"):
            return paged(comments or [])
        if endpoint.endswith("/commits?per_page=100"):
            return paged(commits)
        return paged([pr])

    with (
        patch.dict(
            ci.os.environ,
            {"RUN_HEAD_SHA": pr["head"]["sha"], "RUN_HEAD_BRANCH": pr["head"]["ref"]},
        ),
        patch.object(ci.subprocess, "run"),
        patch.object(ci, "api", side_effect=respond) as client,
        patch.object(ci, "token_owner", return_value="goabonga"),
    ):
        ci.label_dependabot()
    return client


def posted(client: Any, suffix: str) -> list[Any]:
    return [
        c
        for c in client.call_args_list
        if c.args[0].endswith(suffix) and len(c.args) > 1
    ]


def test_a_signed_minor_bump_is_queued_for_merging() -> None:
    client = label_run(dependabot(), [commit(True)])
    assert posted(client, "/issues/5/labels")[0].args[2] == {"labels": ["auto-merge"]}


def test_an_already_queued_pull_request_is_left_alone() -> None:
    client = label_run(dependabot(labels=("auto-merge",)), [commit(True)])
    assert not posted(client, "/issues/5/labels")


def test_unsigned_dependabot_commits_wait_for_the_rewrite() -> None:
    client = label_run(dependabot(), [commit(True), commit(False)])
    assert not posted(client, "/issues/5/labels")


def test_a_major_bump_gets_one_notice_and_waits_for_a_maintainer() -> None:
    major = dependabot(body="Bumps [requests](https://x) from 2.31.0 to 3.0.0.")
    client = label_run(major, [commit(True)])
    assert not posted(client, "/issues/5/labels")
    assert ci.MAJOR_NOTICE in posted(client, "/issues/5/comments")[0].args[2]["body"]
    assert posted(client, "/issues/5/assignees")[0].args[2] == {
        "assignees": ["goabonga"]
    }


def test_a_major_bump_is_announced_only_once() -> None:
    major = dependabot(body="Bumps [requests](https://x) from 2.31.0 to 3.0.0.")
    client = label_run(major, [commit(True)], comments=[{"body": ci.MAJOR_NOTICE}])
    assert not posted(client, "/issues/5/comments")


def test_ci_on_a_stale_head_labels_nothing() -> None:
    stale = dependabot(sha="d" * 40)
    with (
        patch.dict(
            ci.os.environ,
            {"RUN_HEAD_SHA": SHA, "RUN_HEAD_BRANCH": stale["head"]["ref"]},
        ),
        patch.object(ci.subprocess, "run"),
        patch.object(ci, "api", return_value=paged([stale])) as client,
    ):
        ci.label_dependabot()
    assert client.call_count == 1


def test_a_failed_merge_comments_and_drops_the_label(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.argv", ["ci_automation.py", "merge"])
    with (
        patch.object(ci, "merge", side_effect=ValueError("main advanced")),
        patch.object(ci, "api") as client,
        pytest.raises(SystemExit),
    ):
        ci.main()
    methods = [call.args[1] for call in client.call_args_list]
    assert methods == ["POST", "DELETE"]
    assert "main advanced" in client.call_args_list[0].args[2]["body"]


def test_a_failed_command_never_leaks_its_output(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.argv", ["ci_automation.py", "cleanup", "--mode", "resign"])
    failure = subprocess.CalledProcessError(2, ["gpg", "--secret"], output=b"secret")
    with patch.object(ci, "cleanup", side_effect=failure), pytest.raises(SystemExit):
        ci.main()
    assert capsys.readouterr().out == "::error::`gpg` failed with exit status 2\n"


def test_annotations_stay_on_one_line(capsys: pytest.CaptureFixture[str]) -> None:
    ci.annotation("error", "100%\nbad")
    assert capsys.readouterr().out == "::error::100%25%0Abad\n"


def test_the_summary_reports_the_result(
    env: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("JOB_STATUS", "success")
    monkeypatch.setenv("GIT_USER_NAME", "Chris")
    monkeypatch.setenv("GIT_USER_EMAIL", "goabonga@pm.me")
    ci.summary("Signed automatic merge", "Done.")
    text = (tmp_path / "summary").read_text()
    assert "**Result:** success" in text
    assert "Pull request: 9" in text
    assert "Identity: Chris <goabonga@pm.me>" in text
    assert text.endswith("Done.\n")


def test_signing_needs_every_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GPG_PRIVATE_KEY", raising=False)
    with pytest.raises(ValueError, match="Missing GPG_PRIVATE_KEY"):
        ci.configure_signing()


def test_cleanup_only_removes_its_own_signing_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ours, foreign = tmp_path / "ci-signing-1", tmp_path / "other"
    ours.mkdir()
    foreign.mkdir()
    with patch.object(ci.subprocess, "run"):
        monkeypatch.setenv("GNUPGHOME", str(foreign))
        ci.cleanup()
        assert foreign.exists()
        monkeypatch.setenv("GNUPGHOME", str(ours))
        ci.cleanup()
    assert not ours.exists()


def test_an_invalid_repository_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GH_REPO", "not a repository")
    with pytest.raises(ValueError, match="Invalid repository"):
        ci.repository()


def test_an_invalid_sha_is_refused() -> None:
    with pytest.raises(ValueError, match="Invalid commit SHA"):
        ci.validate_head("nope", "feature/x")


def test_paginated_responses_are_decoded_page_by_page() -> None:
    with patch.object(ci, "run", return_value='[{"a": 1}]\n[{"a": 2}]'):
        assert ci.api("x", paginate=True) == [[{"a": 1}], [{"a": 2}]]


def test_an_empty_explicit_token_is_refused() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        ci.api("x", token="")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("feat: add x", "feat: add x\n"),
        ("feat(cli)!: add x", "feat(cli): add x\n"),
        ("remove: drop y", "remove: drop y\n"),
        (
            "fix: a\n\nBody.\nCo-Authored-By: bot <b@x.y>\nBREAKING CHANGE: no\n"
            "Generated with a tool",
            "fix: a\n\nBody.\n",
        ),
    ],
)
def test_commit_messages_are_cleaned(raw: str, expected: str) -> None:
    assert sign.clean_message(raw) == expected


@pytest.mark.parametrize(
    "subject", ["Add x", "feat: Add x", "feat: add x.", "wip: x", "feat: " + "a" * 70]
)
def test_invalid_subjects_are_refused(subject: str) -> None:
    with pytest.raises(SystemExit, match="invalid Conventional Commit"):
        sign.clean_message(subject)
