from unittest.mock import mock_open, patch

import pytest

from generator.main import main

data: str = """
variable "test" {
    default = ""
    type = "string"
}
"""


@pytest.mark.parametrize('option', ('-h', '--help'))
def test_help(capsys, option):
    try:
        main([option])
    except SystemExit:
        pass
    output = capsys.readouterr().out
    assert 'generate terragrunt.hcl confirugation from terraform module' in output


def test_main_local(capsys):
    args = [
        '-u',
        './examples/modules/',
        '-v',
        '0.0.1',
        '-l',
        'test',
    ]
    main(args)

    results = capsys.readouterr().out

    print(results)

    expected = """# modules 0.0.1
# ./examples/modules/
#
# yaml config
# ```
# test:
#   enabled: true
#   # required - required value
#   required: 
#   # optional - optional value
#   # optional: "optional"
#   # nullable - nullable value
#   # nullable: 
# ```
#

include {
    path = find_in_parent_folders()
}

locals {
    source = find_in_parent_folders("./examples/modules/")
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}

terraform {
    source = lookup(local.all, "test", false) == false ? null : lookup(local.all.test, "enabled", false) == false ? null : local.source
}

inputs = merge({
    # required - required value - required
    required = lookup(local.all.test, "required", "")
    # optional - optional value
    optional = lookup(local.all.test, "optional", "optional")
},
  # nullable - nullable value
  (lookup(local.all.test, "nullable", null) == null ? {} : { nullable =  lookup(local.all.test, "nullable") })
)
"""
    assert results == expected


@patch('generator.git.Repo.clone_from')
@patch('os.listdir', return_value=['test.tf'])
@patch('builtins.open', new_callable=mock_open, read_data=data)
def test_main_repo(mock_git, mock_dir, mock_file, capsys):
    args = [
        '-u',
        'https://gitserver.com/test/test.git',
        '-v',
        '0.0.1',
        '-l',
        'test',
    ]
    main(args)

    results = capsys.readouterr().out

    print(results)

    expected = """# test 0.0.1
# https://gitserver.com/test/test/tree/0.0.1/
#
# yaml config
# ```
# test:
#   enabled: true
#   # test - 
#   # # test: 
# ```
#

include {
    path = find_in_parent_folders()
}

locals {
    source = "gitserver.com/test/test.git?ref=0.0.1"
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}

terraform {
    source = lookup(local.all, "test", false) == false ? null : lookup(local.all.test, "enabled", false) == false ? null : local.source
}

inputs = {
    # test - 
    test = lookup(local.all.test, "test", "")
}
"""
    assert results == expected


@patch('generator.git.Repo.clone_from')
@patch('os.listdir', return_value=['test.tf'])
@patch('builtins.open', new_callable=mock_open, read_data=data)
@patch(
    'generator.main.copy_terraform_module',
    side_effect=Exception(b'Test exception message'),
)
@patch('sys.exit')
def test_main_repo_exception(
    mock_exit, mock_copy_module, mock_git, mock_dir, mock_file, capsys
):
    args = [
        '-u',
        'https://gitserver.com/test/test.git',
        '-v',
        '0.0.1',
        '-l',
        'test',
    ]

    main(args)

    results = capsys.readouterr().out

    # Check that the exception message was printed and sys.exit was called
    assert 'Test exception message' in results
    mock_exit.assert_called_once_with(1)
