import os
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


@patch('generator.main.copy_terraform_module')  # empêche la vraie copie
@patch('generator.main.read_directory')  # 👈 patch correct ici
@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
def test_main_local_with_output(
    mock_open_write, mock_makedirs, mock_read_dir, mock_copy_module, tmp_path, capsys
):
    fake_tempdir = tmp_path / "mocked_temp"
    os.makedirs(fake_tempdir.as_posix(), exist_ok=True)

    # Retour simulé du fichier terraform
    mock_read_dir.return_value = {
        'variable': [
            {
                'required': {
                    'description': 'required value',
                    'type': 'string',
                },
                'optional': {
                    'description': 'optional value',
                    'type': 'string',
                    'default': 'optional',
                },
                'nullable': {
                    'description': 'nullable value',
                    'type': 'string',
                    'default': None,
                },
            }
        ]
    }

    with patch(
        'generator.main.create_working_directory', return_value=fake_tempdir.as_posix()
    ):
        args = [
            '-u',
            './examples/modules/',
            '-v',
            '0.0.1',
            '-l',
            'test',
            '-o',
            './output/',
        ]
        main(args)

    results = capsys.readouterr().out
    assert 'terragrunt.hcl written to: ./output/terragrunt.hcl' in results
    # mock_makedirs.assert_called_once_with('./output', exist_ok=True)
    mock_open_write.assert_any_call('./output/terragrunt.hcl', 'w')
    handle = mock_open_write()
    handle.write.assert_called()


@patch('generator.main.copy_terraform_module')
@patch('generator.main.read_directory')
@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
def test_output_explicit_file_path(
    mock_open_write, mock_makedirs, mock_read_dir, mock_copy_module, tmp_path, capsys
):
    output_file = tmp_path / "terragrunt-custom.hcl"

    mock_read_dir.return_value = {
        'variable': [
            {'test': {'description': '', 'type': 'string', 'default': 'value'}}
        ]
    }

    with patch('generator.main.create_working_directory', return_value=str(tmp_path)):
        args = [
            '-u',
            './examples/modules/',
            '-v',
            '0.0.1',
            '-l',
            'test',
            '-o',
            str(output_file),
        ]
        main(args)

    mock_open_write.assert_any_call(str(output_file), 'w')
    handle = mock_open_write()
    handle.write.assert_called()


@patch('generator.main.copy_terraform_module')
@patch('generator.main.read_directory')
@patch('os.makedirs')
@patch('os.path.isdir', return_value=True)  # 👈 important ici
@patch('builtins.open', new_callable=mock_open)
def test_output_directory_without_slash(
    mock_open_write,
    mock_isdir,
    mock_makedirs,
    mock_read_dir,
    mock_copy_module,
    tmp_path,
    capsys,
):
    output_dir = tmp_path / "dir"
    os.makedirs(output_dir)

    mock_read_dir.return_value = {
        'variable': [
            {'test': {'description': '', 'type': 'string', 'default': 'value'}}
        ]
    }

    with patch('generator.main.create_working_directory', return_value=str(tmp_path)):
        args = [
            '-u',
            './examples/modules/',
            '-v',
            '0.0.1',
            '-l',
            'test',
            '-o',
            str(output_dir),  # sans slash
        ]
        main(args)

    expected_path = os.path.join(str(output_dir), 'terragrunt.hcl')
    mock_open_write.assert_any_call(expected_path, 'w')
    handle = mock_open_write()
    handle.write.assert_called()


@patch('generator.main.copy_terraform_module')
@patch('generator.main.read_directory')
@patch('os.makedirs')
@patch('os.path.exists', return_value=True)
@patch(
    'builtins.open',
    new_callable=mock_open,
    read_data="gke:\n  cluster:\n    enabled: true\n",
)
def test_yaml_output_merge_if_exists(
    mock_open_read,
    mock_exists,
    mock_makedirs,
    mock_read_dir,
    mock_copy_module,
    tmp_path,
    capsys,
):
    yaml_output_file = tmp_path / "config.yaml"

    # Ajoute une variable optionnelle pour éviter IndexError dans content_next
    mock_read_dir.return_value = {
        'variable': [
            {
                'helper': {
                    'description': 'helper description',
                    'type': 'string',
                    'default': 'default_value',
                },
                'mandatory_var': {
                    'description': 'mandatory description',
                    'type': 'string',
                },
            }
        ]
    }

    with patch('generator.main.create_working_directory', return_value=str(tmp_path)):
        args = [
            '-u',
            './examples/modules/',
            '-v',
            '0.0.1',
            '-l',
            'gke',
            '--yaml-output',
            str(yaml_output_file),
        ]
        main(args)

    results = capsys.readouterr().out
    assert f"YAML config written to: {yaml_output_file}" in results

    mock_open_read.assert_any_call(str(yaml_output_file), 'r')
    mock_open_read.assert_any_call(str(yaml_output_file), 'w')
    handle = mock_open_read()
    handle.write.assert_called()


@patch('generator.main.copy_terraform_module')
@patch('generator.main.read_directory')
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)  # 👈 le fichier n'existe PAS
@patch('builtins.open', new_callable=mock_open)
def test_yaml_output_new_file_creation(
    mock_open_write,
    mock_exists,
    mock_makedirs,
    mock_read_dir,
    mock_copy_module,
    tmp_path,
    capsys,
):
    yaml_output_file = tmp_path / "config.yaml"

    # Une seule variable suffit ici
    mock_read_dir.return_value = {
        'variable': [
            {
                'test': {
                    'description': 'desc',
                    'type': 'string',
                    'default': 'default_val',
                }
            }
        ]
    }

    with patch('generator.main.create_working_directory', return_value=str(tmp_path)):
        args = [
            '-u',
            './examples/modules/',
            '-v',
            '0.0.1',
            '-l',
            'gke',
            '--yaml-output',
            str(yaml_output_file),
        ]
        main(args)

    results = capsys.readouterr().out
    assert f"YAML config written to: {yaml_output_file}" in results

    mock_open_write.assert_any_call(str(yaml_output_file), 'w')
    handle = mock_open_write()
    handle.write.assert_called()
