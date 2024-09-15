import argparse
import sys
from shutil import copytree
from tempfile import gettempdir
from uuid import uuid4

from generator import __version__
from generator.generate import generate
from generator.git import clone
from generator.reader import read_directory
from generator.utils import is_local

parser = argparse.ArgumentParser(
    prog='terragrunt-gernerator',
    description='generate terragrunt.hcl confirugation' + ' from terraform module',
)

parser.add_argument(
    '-V',
    action='version',
    version=f'%(prog)s {__version__}',
)

parser.add_argument('-u', '--url', required=True, help='the module repository url')

parser.add_argument('-v', '--version', help='the module version to use', default='main')

parser.add_argument('-p', '--path', help='define the module path if needed')

parser.add_argument(
    '--include',
    help='do no rendering the include block',
    action=argparse.BooleanOptionalAction,
    default=True,
)

parser.add_argument('-l', '--lookup', help='define the lookup path', required=True)


def create_working_directory() -> str:
    tempdir = f'{gettempdir()}/{uuid4()}'
    return tempdir


def copy_terraform_module(url: str, version: str, path: str):
    if is_local(url):
        copytree(url, path)
    else:
        clone(url, path, version)


def main(args=None):
    args: map = parser.parse_args(args)

    tempdir: str = create_working_directory()
    try:
        copy_terraform_module(args.url, args.version, tempdir)
    except BaseException as e:
        print(e.args[-1:][0].decode())
        sys.exit(1)

    hcl_files: dict = read_directory(
        f"{tempdir}/{'' if args.path is None else args.path}"
    )

    output: str = generate(
        args.url,
        None if args.path is None else args.path,
        args.version,
        args.lookup,
        hcl_files,
        args.include,
    )

    print(output)
