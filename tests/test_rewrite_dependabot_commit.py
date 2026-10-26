# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import importlib.util
import subprocess
from pathlib import Path
from typing import Any

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "rewrite_dependabot_commit.py"
spec = importlib.util.spec_from_file_location("rewrite_dependabot_commit", SCRIPT)
assert spec is not None and spec.loader is not None
rewrite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rewrite)


@pytest.fixture
def pyproject(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _ = (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["requests>=2", "Some_Lib[extra]~=1.0", "a;python_version<\'3.12\'"]\n'
        '[dependency-groups]\ndev = ["ruff>=0.13"]\nfavicon = ["pillow>=10"]\n'
    )
    monkeypatch.chdir(tmp_path)


@pytest.mark.parametrize(
    ("spec", "name"),
    [
        ("ruff>=0.13", "ruff"),
        ("Some_Tool[extra]~=1.0", "some-tool"),
        ("a;python_version<'3.12'", "a"),
        ("b", "b"),
    ],
)
def test_requirement_name(spec: str, name: str) -> None:
    assert rewrite.requirement_name(spec) == name


@pytest.mark.parametrize(
    ("package", "expected"),
    [
        ("requests", True),
        ("some_lib", True),
        ("a", True),
        ("ruff", False),
        ("pillow", False),
        ("virtualenv", False),
    ],
)
@pytest.mark.usefixtures("pyproject")
def test_is_runtime_dependency(package: str, expected: bool) -> None:
    assert rewrite.is_runtime_dependency(package) is expected


def test_without_runtime_dependencies_nothing_is_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _ = (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    monkeypatch.chdir(tmp_path)
    assert not rewrite.is_runtime_dependency("requests")


@pytest.mark.parametrize(
    ("changed", "text", "expected"),
    [
        ([".github/workflows/ci.yml"], "bump actions/checkout from 6 to 7", "ci"),
        (["uv.lock"], "bump the dev-tools group with 2 updates", "chore(deps)"),
        (["uv.lock"], "bump ruff from 0.1 to 0.2", "chore(deps)"),
        (["uv.lock"], "bump pillow from 12 to 13", "chore(deps)"),
        (["uv.lock"], "bump virtualenv from 20 to 21", "chore(deps)"),
        (["uv.lock"], "bump requests from 1 to 2", "fix(deps)"),
        (["uv.lock"], "update something", "chore(deps)"),
    ],
)
@pytest.mark.usefixtures("pyproject")
def test_commit_type(changed: list[str], text: str, expected: str) -> None:
    assert rewrite.commit_type(changed, text) == expected


@pytest.mark.usefixtures("pyproject")
def test_rewrite_normalizes_the_subject_and_drops_co_authors() -> None:
    message = rewrite.rewrite(
        ["uv.lock"],
        "build(deps): bump requests from 1 to 2",
        "Details.\nCo-authored-by: bot <b@x.y>\n",
    )
    assert message == "fix(deps): bump requests from 1 to 2\n\nDetails."


@pytest.mark.usefixtures("pyproject")
def test_rewrite_without_a_body() -> None:
    assert (
        rewrite.rewrite(["uv.lock"], "Bump ruff from 1 to 2", "")
        == "chore(deps): Bump ruff from 1 to 2"
    )


@pytest.mark.usefixtures("pyproject")
def test_main_amends_the_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = {
        ("show", "--name-only", "--pretty=", "HEAD"): "uv.lock\n",
        ("log", "-1", "--pretty=%s", "HEAD"): "Bump requests from 1 to 2",
        ("log", "-1", "--pretty=%b", "HEAD"): "",
    }
    monkeypatch.setattr(rewrite, "git", lambda *args: answers[args])
    calls: list[Any] = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: calls.append((a[0], k)))
    rewrite.main()
    assert calls == [
        (
            [
                "git",
                "commit",
                "--amend",
                "--reset-author",
                "-m",
                "fix(deps): Bump requests from 1 to 2",
                "--quiet",
            ],
            {"check": True},
        )
    ]


def test_git_returns_stripped_output() -> None:
    assert rewrite.git("--version").startswith("git version")
