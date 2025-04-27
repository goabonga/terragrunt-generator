import argparse
import os
import sys
from pathlib import Path
from shutil import copytree
from tempfile import gettempdir
from uuid import uuid4

from generator import __name__, __version__
from generator.generate import generate
from generator.git import clone
from generator.reader import read_directory
from generator.utils import is_local
from generator.yaml import merge_yaml_strings

parser = argparse.ArgumentParser(
    prog=__name__,
    description='Generate a terragrunt.hcl configuration file from a Terraform module.',
)

parser.add_argument(
    '-V',
    action='version',
    version=f'%(prog)s {__version__}',
)

parser.add_argument(
    '-u',
    '--url',
    required=True,
    help='URL or local path to the Terraform module (can be a git repo or directory).',
)

parser.add_argument(
    '-v',
    '--version',
    help='Branch, tag, or commit hash to checkout if the module is from a git repository (default: main).',
    default='main',
)

parser.add_argument(
    '-p',
    '--path',
    help='Relative path to the module inside the repository or directory (if needed).',
)

parser.add_argument(
    '--include',
    help='Whether to include the "include" block in the generated terragrunt.hcl (default: true).',
    action=argparse.BooleanOptionalAction,
    default=True,
)

parser.add_argument(
    '-l',
    '--lookup',
    required=True,
    help='Path used for variable lookup in the generated Terragrunt configuration.',
)

parser.add_argument(
    '-o',
    '--output',
    help='File path to write the generated terragrunt.hcl (default: print to stdout).',
    default=None,
)

parser.add_argument(
    '--yaml-output',
    help='Directories to write the generated YAML config file (can be specified multiple times).',
    action='append',
    default=[],
)

parser.add_argument(
    '--yaml-for-env',
    help='Environment names used to generate YAML files (e.g., dev, prod).',
    action='append',
    default=[],
)

parser.add_argument(
    '--enabled',
    help='Whether to mark the module as enabled in the YAML configuration (default: true).',
    action=argparse.BooleanOptionalAction,
    default=True,
)


def create_working_directory() -> str:
    tempdir = f'{gettempdir()}/{uuid4()}'
    return tempdir


def copy_terraform_module(url: str, version: str, path: str):
    if is_local(url):
        copytree(url, path)
    else:
        clone(url, path, version)


def write_hcl_file(args, output):

    if args.output.endswith('/') or not os.path.splitext(args.output)[1]:
        output_path = os.path.join(args.output, 'terragrunt.hcl')
    else:
        output_path = args.output

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(output)

    print(f"terragrunt.hcl written to: {output_path}")


def main(args=None):
    args: map = parser.parse_args(args)

    tempdir: str = create_working_directory()
    try:
        copy_terraform_module(args.url, args.version, tempdir)
    except BaseException as e:
        print(str(e))
        sys.exit(1)

    hcl_files: dict = read_directory(
        f"{tempdir}/{'' if args.path is None else args.path}"
    )

    output, yanl = generate(
        url=args.url,
        path=None if args.path is None else args.path,
        version=args.version,
        lookup=args.lookup,
        hcl_files=hcl_files,
        include=args.include,
        config_filename=(
            f"config.{args.yaml_for_env}.yaml"
            if len(args.yaml_for_env) > 0
            else (
                os.path.basename(args.yaml_output[0])
                if len(args.yaml_output) > 0
                else "config.yaml"
            )
        ),
        yaml_env=args.yaml_for_env[0] if len(args.yaml_for_env) > 0 else None,
        enabled=args.enabled,
    )

    for yaml_output in args.yaml_output:
        yaml_output_path = Path(yaml_output)

        envs = args.yaml_for_env if args.yaml_for_env else [None]

        for env in envs:
            if yaml_output_path.is_dir() or str(yaml_output_path).endswith('/'):
                config_filename = f"config.{env}.yaml" if env else "config.yaml"
                final_path = yaml_output_path / config_filename
            else:
                # cas où l'utilisateur donne directement un fichier
                if env:
                    final_path = yaml_output_path.parent / f"config.{env}.yaml"
                else:
                    final_path = yaml_output_path

            final_path.parent.mkdir(parents=True, exist_ok=True)

            if final_path.exists():
                with final_path.open('r') as f:
                    existing_yaml = f.read()
                final_yaml = merge_yaml_strings(existing_yaml, yanl)
            else:
                final_yaml = yanl

            with final_path.open('w') as f:
                f.write(final_yaml)

            print(f"YAML config written to: {final_path}")

    if args.output is not None:
        write_hcl_file(args, output)
    else:
        print(output)
