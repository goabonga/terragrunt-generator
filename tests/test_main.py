# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

from pathlib import Path
from unittest.mock import patch

import pytest

from terragrunt_generator.main import (
    build_parser,
    config_filename,
    main,
    write_hcl_file,
    write_yaml,
    yaml_target,
)


def test_the_parser_defaults():
    args = build_parser().parse_args(["-u", "mod", "-l", "a"])

    assert args.url == "mod"
    assert args.lookup == "a"
    assert args.version == "main"
    assert args.path is None
    assert args.output is None
    assert args.include is True
    assert args.enabled is True
    assert args.yaml_output == []
    assert args.yaml_for_env == []


def test_the_parser_collects_repeated_options():
    args = build_parser().parse_args(
        [
            "-u",
            "mod",
            "-l",
            "a",
            "--yaml-output",
            "x",
            "--yaml-output",
            "y",
            "--yaml-for-env",
            "dev",
            "--yaml-for-env",
            "prod",
            "--no-include",
            "--no-enabled",
        ]
    )

    assert args.yaml_output == ["x", "y"]
    assert args.yaml_for_env == ["dev", "prod"]
    assert args.include is False
    assert args.enabled is False


def test_each_call_builds_its_own_parser():
    assert build_parser() is not build_parser()


@pytest.mark.parametrize("missing", [["-l", "a"], ["-u", "mod"]])
def test_the_url_and_the_lookup_are_required(missing):
    with pytest.raises(SystemExit):
        build_parser().parse_args(missing)


@pytest.mark.parametrize(
    ("yaml_for_env", "yaml_output", "expected"),
    [
        ([], [], "config.yaml"),
        ([], ["out/special.yaml", "other.yaml"], "special.yaml"),
        (["dev"], [], "config.dev.yaml"),
        (["dev", "prod"], ["out/special.yaml"], "config.dev.yaml"),
    ],
)
def test_config_filename(yaml_for_env, yaml_output, expected):
    assert config_filename(yaml_for_env, yaml_output) == expected


def test_a_directory_gets_the_default_config(tmp_path: Path):
    assert yaml_target(str(tmp_path), None) == tmp_path / "config.yaml"
    assert yaml_target(str(tmp_path), "dev") == tmp_path / "config.dev.yaml"


def test_a_file_is_used_as_given(tmp_path: Path):
    assert yaml_target(str(tmp_path / "c.yaml"), None) == tmp_path / "c.yaml"


def test_an_environment_renames_a_file_next_to_itself(tmp_path: Path):
    assert yaml_target(str(tmp_path / "c.yaml"), "dev") == tmp_path / "config.dev.yaml"


def test_write_yaml_creates_the_directories(tmp_path: Path, capsys):
    target = tmp_path / "a" / "b" / "config.yaml"

    write_yaml(target, "a:\n  enabled: true\n")

    assert target.read_text() == "a:\n  enabled: true\n"
    assert capsys.readouterr().out == f"YAML config written to: {target}\n"


def test_write_yaml_merges_into_an_existing_file(tmp_path: Path):
    target = tmp_path / "config.yaml"
    target.write_text("a:\n  enabled: false\n  # kept\n")

    write_yaml(target, "a:\n  enabled: true\n  # new\n")

    merged = target.read_text()
    assert "enabled: false" in merged
    assert "# kept" in merged
    assert "# new" in merged


@pytest.mark.parametrize("output", ["{dir}/", "{dir}/sub", "{dir}/sub/"])
def test_write_hcl_file_puts_a_directory_output_in_terragrunt_hcl(
    tmp_path: Path, capsys, output
):
    write_hcl_file(output.format(dir=tmp_path), "content")

    written = Path(output.format(dir=tmp_path)) / "terragrunt.hcl"
    assert written.read_text() == "content"
    assert capsys.readouterr().out == f"terragrunt.hcl written to: {written}\n"


def test_write_hcl_file_writes_a_file_output_as_given(tmp_path: Path):
    write_hcl_file(str(tmp_path / "x" / "my.hcl"), "content")

    assert (tmp_path / "x" / "my.hcl").read_text() == "content"


def run_main(tmp_path: Path, fetch_error: BaseException | None = None) -> Path:
    work = tmp_path / "work"
    work.mkdir()
    (work / "main.tf").write_text("")

    with (
        patch(
            "terragrunt_generator.main.create_working_directory", return_value=str(work)
        ),
        patch("terragrunt_generator.main.module_source") as source,
        patch("terragrunt_generator.main.read_directory", return_value={}),
    ):
        source.return_value.fetch.side_effect = fetch_error
        main(["-u", "https://gitserver.com/test/test.git", "-l", "test"])
    return work


def test_the_working_directory_is_removed_once_the_output_is_written(tmp_path: Path):
    work = run_main(tmp_path)

    assert not work.exists()


def test_the_working_directory_is_removed_when_the_module_cannot_be_fetched(
    tmp_path: Path,
):
    work = tmp_path / "work"
    with pytest.raises(SystemExit):
        run_main(tmp_path, fetch_error=Exception("no such repository"))

    assert not work.exists()


def test_an_interruption_is_not_swallowed(tmp_path: Path):
    work = tmp_path / "work"
    with pytest.raises(KeyboardInterrupt):
        run_main(tmp_path, fetch_error=KeyboardInterrupt())

    assert not work.exists()
