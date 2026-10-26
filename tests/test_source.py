# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

from pathlib import Path
from unittest.mock import patch

import pytest

from terragrunt_generator.source import (
    GitSource,
    LocalSource,
    ModuleSource,
    module_source,
)

REPO = "https://gitserver.com/test/test.git"


def test_a_directory_that_exists_is_a_local_source(tmp_path: Path):
    assert isinstance(module_source(str(tmp_path), "main"), LocalSource)


@pytest.mark.parametrize(
    "url", [REPO, "git@gitserver.com:test/test.git", "/nonexistent"]
)
def test_anything_else_is_a_git_source(url):
    assert isinstance(module_source(url, "main"), GitSource)


def test_the_source_keeps_what_it_was_given():
    source = module_source(REPO, "1.2.3", "modules/test")

    assert (source.url, source.version, source.path) == (REPO, "1.2.3", "modules/test")


def test_the_base_class_cannot_be_instantiated():
    with pytest.raises(TypeError):
        ModuleSource(REPO, "main")  # type: ignore[abstract]


@patch("terragrunt_generator.source.clone")
def test_a_git_source_clones_the_version_into_the_destination(clone):
    GitSource(REPO, "0.1.0").fetch("/work/module")

    clone.assert_called_once_with(REPO, "/work/module", "0.1.0")


def test_a_local_source_copies_the_directory(tmp_path: Path):
    origin = tmp_path / "origin"
    origin.mkdir()
    (origin / "main.tf").write_text("variable {}")

    LocalSource(str(origin), "main").fetch(str(tmp_path / "copy"))

    assert (tmp_path / "copy" / "main.tf").read_text() == "variable {}"


@pytest.mark.parametrize(
    ("url", "path", "name"),
    [
        (REPO, "modules/test", "test"),
        (REPO, "single", "single"),
        ("https://gitserver.com/org/repo.git", None, "org"),
        ("modules/network", None, "modules"),
        ("network", None, ""),
    ],
)
def test_the_name(url, path, name):
    assert GitSource(url, "main", path).name == name


@pytest.mark.parametrize(
    ("url", "path", "web_url"),
    [
        (REPO, None, "https://gitserver.com/test/test/tree/0.1.0/"),
        (
            REPO,
            "modules/test",
            "https://gitserver.com/test/test/tree/0.1.0/modules/test",
        ),
        ("../local/module", "modules/test", "../local/module"),
    ],
)
def test_the_web_url_links_the_module_page(url, path, web_url):
    assert GitSource(url, "0.1.0", path).web_url == web_url


@pytest.mark.parametrize(
    ("url", "path", "source"),
    [
        (REPO, None, '"gitserver.com/test/test.git?ref=0.1.0"'),
        (REPO, "modules/test", '"gitserver.com/test/test.git//modules/test?ref=0.1.0"'),
        ("http://gitserver.com/test/test", None, '"gitserver.com/test/test?ref=0.1.0"'),
        ("../local/module", None, 'find_in_parent_folders("../local/module")'),
        ("../local/module", "ignored", 'find_in_parent_folders("../local/module")'),
    ],
)
def test_the_terragrunt_source(url, path, source):
    assert GitSource(url, "0.1.0", path).terragrunt_source == source


def test_an_empty_path_is_still_a_sub_path():
    # Kept from the generator before the source object: an empty path is not "no path".
    assert GitSource(REPO, "1", "").terragrunt_source.endswith('//?ref=1"')
