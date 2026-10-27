# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location(
    "check_commit_subject", SCRIPTS / "check_commit_subject.py"
)
assert spec is not None and spec.loader is not None
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

LONG = "test: cover " + "x" * 61


@pytest.mark.parametrize(
    "subject",
    [
        "fix: handle an empty plan",
        "feat(cli): add a flag",
        "refactor!: drop the old api",
        "chore(deps): bump ruff from 1 to 2",
        "test: " + "x" * 66,
    ],
)
def test_valid_subjects(subject: str) -> None:
    assert check.problem(subject) is None


@pytest.mark.parametrize(
    ("subject", "reason"),
    [
        (LONG, "73 characters"),
        ("fix: handle an empty plan.", "period"),
        ("Fix: handle an empty plan", "known type"),
        ("fix: Handle an empty plan", "known type"),
        ("wip: handle an empty plan", "known type"),
        ("handle an empty plan", "known type"),
        ("", "known type"),
    ],
)
def test_invalid_subjects(subject: str, reason: str) -> None:
    assert reason in check.problem(subject)


def test_the_subject_of_a_message_file_skips_comments(tmp_path: Path) -> None:
    message = tmp_path / "COMMIT_EDITMSG"
    message.write_text("\n# Please enter the commit message\nfix: a change\n\nbody\n")
    assert check.message_subject(str(message)) == "fix: a change"


@pytest.mark.parametrize("prefix", ["fixup! ", "squash! ", "amend! "])
def test_the_hook_lets_autosquash_commits_through(tmp_path: Path, prefix: str) -> None:
    message = tmp_path / "COMMIT_EDITMSG"
    message.write_text(f"{prefix}fix: a change that is squashed away later on.\n")
    assert check.main([str(message)]) == 0


def test_an_empty_message_file_has_no_subject(tmp_path: Path) -> None:
    message = tmp_path / "COMMIT_EDITMSG"
    message.write_text("# only a comment\n")
    assert check.message_subject(str(message)) == ""


def test_the_hook_mode_checks_the_message_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    message = tmp_path / "COMMIT_EDITMSG"
    message.write_text("fix: a change\n")
    assert check.main([str(message)]) == 0
    message.write_text(LONG + "\n")
    assert check.main([str(message)]) == 1
    assert "73 characters" in capsys.readouterr().out


def test_the_range_mode_reports_every_invalid_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)

    def git(*args: str) -> None:
        subprocess.run(["git", *args], check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("config", "user.name", "Chris")
    git("config", "user.email", "chris@example.org")
    git("config", "commit.gpgsign", "false")
    git("commit", "-q", "--allow-empty", "-m", "chore: base")
    for subject in ("fix: a change", "Fix: a change.", LONG):
        git("commit", "-q", "--allow-empty", "-m", subject)
    assert check.main(["--range", "HEAD~3..HEAD"]) == 1
    out = capsys.readouterr().out
    assert "a change.'" in out and "73 characters" in out
    assert "'fix: a change'" not in out
    assert check.main(["--range", "HEAD~3..HEAD~2"]) == 0


def test_arguments_are_validated(capsys: pytest.CaptureFixture[str]) -> None:
    assert check.main([]) == 2
    assert check.main(["--range"]) == 2
    assert "usage" in capsys.readouterr().out
