# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import argparse
import os
import sys
from pathlib import Path
from tempfile import gettempdir
from typing import Any
from uuid import uuid4

from terragrunt_generator import __prog__, __version__
from terragrunt_generator.generate import generate
from terragrunt_generator.reader import read_directory
from terragrunt_generator.source import module_source
from terragrunt_generator.yaml import merge_yaml_strings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description="Generate a terragrunt.hcl configuration file from a Terraform module.",
    )

    parser.add_argument(
        "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-u",
        "--url",
        required=True,
        help="URL or local path to the Terraform module (can be a git repo or directory).",
    )

    parser.add_argument(
        "-v",
        "--version",
        help="Branch, tag, or commit hash to checkout if the module is from a git repository (default: main).",
        default="main",
    )

    parser.add_argument(
        "-p",
        "--path",
        help="Relative path to the module inside the repository or directory (if needed).",
    )

    parser.add_argument(
        "--include",
        help='Whether to include the "include" block in the generated terragrunt.hcl (default: true).',
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "-l",
        "--lookup",
        required=True,
        help="Path used for variable lookup in the generated Terragrunt configuration.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="File path to write the generated terragrunt.hcl (default: print to stdout).",
        default=None,
    )

    parser.add_argument(
        "--yaml-output",
        help="Directories to write the generated YAML config file (can be specified multiple times).",
        action="append",
        default=[],
    )

    parser.add_argument(
        "--yaml-for-env",
        help="Environment names used to generate YAML files (e.g., dev, prod).",
        action="append",
        default=[],
    )

    parser.add_argument(
        "--enabled",
        help="Whether to mark the module as enabled in the YAML configuration (default: true).",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    return parser


def create_working_directory() -> str:
    tempdir = f"{gettempdir()}/{uuid4()}"
    return tempdir


def config_filename(yaml_for_env: list[str], yaml_output: list[str]) -> str:
    """The name of the config file that the generated locals read."""
    if yaml_for_env:
        return f"config.{yaml_for_env[0]}.yaml"
    if yaml_output:
        return os.path.basename(yaml_output[0])
    return "config.yaml"


def yaml_target(output: str, env: str | None) -> Path:
    """The file a YAML config is written to for ``--yaml-output`` and an environment.

    A directory gets ``config.yaml``, or ``config.<env>.yaml`` for an environment;
    a file is used as given, unless an environment renames it next to itself.
    """
    path = Path(output)
    if path.is_dir() or str(path).endswith("/"):
        return path / (f"config.{env}.yaml" if env else "config.yaml")
    if env:
        return path.parent / f"config.{env}.yaml"
    return path


def write_yaml(path: Path, content: str) -> None:
    """Write the YAML config, merged into the file when it already exists."""
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        with path.open("r") as f:
            content = merge_yaml_strings(f.read(), content)

    with path.open("w") as f:
        f.write(content)

    print(f"YAML config written to: {path}")


def write_hcl_file(output: str, content: str) -> None:
    if output.endswith("/") or not os.path.splitext(output)[1]:
        output_path = os.path.join(output, "terragrunt.hcl")
    else:
        output_path = output

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(content)

    print(f"terragrunt.hcl written to: {output_path}")


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    tempdir: str = create_working_directory()
    try:
        module_source(args.url, args.version).fetch(tempdir)
    except Exception as e:
        print(str(e))
        sys.exit(1)

    hcl_files: dict[str, Any] = read_directory(f"{tempdir}/{args.path or ''}")

    output, yaml_config = generate(
        url=args.url,
        path=args.path,
        version=args.version,
        lookup=args.lookup,
        hcl_files=hcl_files,
        include=args.include,
        config_filename=config_filename(args.yaml_for_env, args.yaml_output),
        yaml_env=args.yaml_for_env[0] if args.yaml_for_env else None,
        enabled=args.enabled,
    )

    for yaml_output in args.yaml_output:
        for env in args.yaml_for_env or [None]:
            write_yaml(yaml_target(yaml_output, env), yaml_config)

    if args.output is not None:
        write_hcl_file(args.output, output)
    else:
        print(output)
