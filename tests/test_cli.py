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

    expected = """#  0.0.1
# ./examples/modules//tree/0.0.1/
#
# yaml config
# ```
# test:
#   enabled: true
#   # required - required value
#   required: 
#   # optional - optional value
#   optional: "optional"
#   # nullable - nullable value
#   # nullable: 
# ```
#

include {
    path = find_in_parent_folders()
}

locals {
    module = {
        repository = "./examples/modules/"
        path = null
        version = "0.0.1"
        source =  "${local.module.repository}${local.module.path != null ? local.module.path : ''}?ref=${local.module.version}"
    }
    environment = get_env("CONFIG", "test")
    all = merge(
        yamldecode(file(find_in_parent_folders(format("config.%s.yaml", local.environment)))),
    )
}

terraform {
    source = lookup(local.all.test, "enabled", true) == true ? local.module.source : null
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
#   test: 
# ```
#

include {
    path = find_in_parent_folders()
}

locals {
    module = {
        repository = "gitserver.com/test/test.git"
        path = null
        version = "0.0.1"
        source =  "${local.module.repository}${local.module.path != null ? local.module.path : ''}?ref=${local.module.version}"
    }
    environment = get_env("CONFIG", "test")
    all = merge(
        yamldecode(file(find_in_parent_folders(format("config.%s.yaml", local.environment)))),
    )
}

terraform {
    source = lookup(local.all.test, "enabled", true) == true ? local.module.source : null
}

inputs = {
    # test - 
    test = lookup(local.all.test, "test", "")
}
"""
    assert results == expected
