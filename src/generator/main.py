import argparse
from tempfile import gettempdir
from uuid import uuid4

from generator.generate import generate
from generator.git import clone
from generator.reader import read_directory


def main():
    parser = argparse.ArgumentParser(
        prog='terragrunt-gernerator',
        description='generate terragrunt.hcl confirugation'
        + ' from terraform module',
    )
    parser.add_argument(
        '-u', '--url', required=True, help='the module repository url'
    )
    parser.add_argument(
        '-v', '--version', required=True, help='the module version to use'
    )
    parser.add_argument(
        '-p', '--path', help='define the module path if needed'
    )
    parser.add_argument(
        '--include', help='do no rendering the include block',
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        '-c', '--config', help='define the yaml config path', default="find_in_parent_folders(\"config.yaml\")"
    )
    parser.add_argument(
        '-l', '--lookup', help='define the lookup path', default="[\"{name}\"]"
    )

    args = parser.parse_args()

    tempdir = f'{gettempdir()}/{uuid4()}'

    clone(args.url, tempdir, args.version)

    variables: list = read_directory(
        f"{tempdir}//{'' if args.path is None else args.path}"
    )

    output: str = generate(
        args.url,
        None if args.path is None else args.path,
        args.version,
        variables,
        args.include,
        args.config,
        args.lookup
    )

    print(output)
