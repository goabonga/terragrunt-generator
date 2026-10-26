# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPTS = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location(
    "split_dependabot_lock", SCRIPTS / "split_dependabot_lock.py"
)
assert spec is not None and spec.loader is not None
split = importlib.util.module_from_spec(spec)
spec.loader.exec_module(split)

PYPROJECT = (
    '[project]\nname = "demo"\nversion = "1.0.0"\ndependencies = ["requests>=2"]\n'
    '[dependency-groups]\ndev = ["ruff>=0.1", "pytest>=8", {include-group = "docs"}]\n'
    'docs = ["zensical>=0.1"]\n'
)


def lock(**versions: str) -> str:
    blocks = "".join(
        f'\n[[package]]\nname = "{name}"\nversion = "{version}"\n'
        for name, version in versions.items()
    )
    return f"version = 1\n{blocks}"


BASE = lock(
    demo="1.0.0", requests="2.0", ruff="0.1", pytest="8.0", zensical="0.1", idna="3.0"
)
HEAD = lock(
    demo="1.0.0", requests="2.1", ruff="0.2", pytest="8.1", zensical="0.2", idna="3.0"
)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    (tmp_path / "repo").mkdir()
    monkeypatch.chdir(tmp_path / "repo")
    git("init", "-q", "-b", "main")
    git("config", "user.name", "Chris")
    git("config", "user.email", "chris@example.org")
    git("config", "commit.gpgsign", "false")
    _ = Path("pyproject.toml").write_text(PYPROJECT)
    _ = Path("uv.lock").write_text(BASE)
    git("add", "pyproject.toml", "uv.lock")
    git("commit", "-q", "-m", "chore: base")
    base = git("rev-parse", "HEAD")
    _ = Path("uv.lock").write_text(HEAD)
    git("commit", "-q", "-am", "chore(deps): bump the dev-tools group")
    return base


@pytest.fixture
def uv(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """A uv that moves one package of the lock to the requested version."""
    calls: list[str] = []

    def upgrade(name: str, version: str) -> None:
        calls.append(f"{name}=={version}")
        text = Path("uv.lock").read_text()
        current = split.locked_versions(text)[name][0]
        _ = Path("uv.lock").write_text(
            text.replace(
                f'name = "{name}"\nversion = "{current}"',
                f'name = "{name}"\nversion = "{version}"',
            )
        )

    monkeypatch.setattr(split, "upgrade", upgrade)
    return calls


def test_locked_versions_lists_every_version_of_a_package() -> None:
    text = lock(a="1") + '\n[[package]]\nname = "A"\nversion = "2"\n'
    assert split.locked_versions(text) == {"a": ["1", "2"]}


@pytest.mark.usefixtures("repo")
def test_declared_packages_cover_the_project_and_its_groups() -> None:
    assert split.declared_packages() == {"requests", "ruff", "pytest", "zensical"}


def test_updates_keep_declared_packages_whose_version_moved() -> None:
    moved = split.updates(BASE, HEAD, {"ruff", "pytest", "idna", "absent"})
    assert moved == [("pytest", "8.0", "8.1"), ("ruff", "0.1", "0.2")]


def test_a_package_locked_twice_is_not_split() -> None:
    twice = lock(ruff="0.1") + '\n[[package]]\nname = "ruff"\nversion = "0.0"\n'
    assert split.updates(twice, lock(ruff="0.2"), {"ruff"}) == []


@pytest.mark.usefixtures("repo")
def test_runtime_dependencies_come_first() -> None:
    moved = [("pytest", "1", "2"), ("requests", "1", "2"), ("ruff", "1", "2")]
    assert [name for name, *_ in split.runtime_first(moved)] == [
        "requests",
        "pytest",
        "ruff",
    ]


@pytest.mark.usefixtures("repo")
def test_the_type_follows_the_runtime_membership() -> None:
    assert split.subject("requests", "1", "2") == "fix(deps): bump requests from 1 to 2"
    assert split.subject("ruff", "1", "2") == "chore(deps): bump ruff from 1 to 2"


@pytest.mark.usefixtures("uv")
def test_prepare_stores_one_lock_per_dependency(repo: str, tmp_path: Path) -> None:
    out = tmp_path / "out"
    assert split.prepare(repo, str(out)) == 4
    assert [path.name for path in sorted(out.glob("*.msg"))] == [
        f"{n:02}.msg" for n in range(1, 5)
    ]
    assert (out / "01.msg").read_text() == "fix(deps): bump requests from 2.0 to 2.1"
    assert (out / "base").read_text() == repo
    assert Path("uv.lock").read_text() == HEAD
    assert git("status", "--porcelain") == ""


def test_prepare_upgrades_cumulatively(
    repo: str, uv: list[str], tmp_path: Path
) -> None:
    _ = split.prepare(repo, str(tmp_path / "out"))
    assert uv == ["requests==2.1", "pytest==8.1", "ruff==0.2", "zensical==0.2"]
    first = split.locked_versions((tmp_path / "out" / "01.lock").read_text())
    assert first["requests"] == ["2.1"] and first["ruff"] == ["0.1"]


@pytest.mark.usefixtures("uv")
def test_a_head_changing_more_than_the_lock_is_not_split(
    repo: str, tmp_path: Path
) -> None:
    _ = Path("pyproject.toml").write_text(PYPROJECT + "# touched\n")
    git("commit", "-q", "-am", "chore: touch")
    assert split.prepare(repo, str(tmp_path / "out")) == 0


@pytest.mark.usefixtures("uv")
def test_a_single_dependency_is_not_split(repo: str, tmp_path: Path) -> None:
    _ = Path("uv.lock").write_text(
        lock(demo="1.0.0", requests="2.1", ruff="0.1", pytest="8.0")
    )
    git("commit", "-q", "-am", "chore: one bump")
    assert split.prepare(repo, str(tmp_path / "out")) == 0


@pytest.mark.usefixtures("uv")
def test_a_regenerated_lock_that_differs_is_not_split(
    repo: str, tmp_path: Path
) -> None:
    _ = Path("uv.lock").write_text(HEAD.replace('"3.0"', '"3.1"'))
    git("commit", "-q", "-am", "chore: transitive")
    assert split.prepare(repo, str(tmp_path / "out")) == 0
    assert git("status", "--porcelain") == ""


def test_a_failing_uv_is_not_split(
    repo: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(name: str, version: str) -> None:
        raise subprocess.CalledProcessError(1, "uv")

    monkeypatch.setattr(split, "upgrade", fail)
    assert split.prepare(repo, str(tmp_path / "out")) == 0
    assert Path("uv.lock").read_text() == HEAD


@pytest.mark.usefixtures("uv")
def test_commit_replays_one_commit_per_dependency(repo: str, tmp_path: Path) -> None:
    out = str(tmp_path / "out")
    _ = split.prepare(repo, out)
    split.commit(out)
    assert git("log", "--reverse", "--pretty=%s", f"{repo}..HEAD").splitlines() == [
        "fix(deps): bump requests from 2.0 to 2.1",
        "chore(deps): bump pytest from 8.0 to 8.1",
        "chore(deps): bump ruff from 0.1 to 0.2",
        "chore(deps): bump zensical from 0.1 to 0.2",
    ]
    assert Path("uv.lock").read_text() == HEAD


def test_upgrade_pins_the_requested_version(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Any] = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: calls.append((a[0], k)))
    split.upgrade("ruff", "0.2")
    assert calls[0][0] == ["uv", "lock", "--upgrade-package", "ruff==0.2"]
