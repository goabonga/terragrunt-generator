from generator.generate import (
    generate_include,
    generate_inputs,
    generate_locals,
    generate_terraform,
)


def test_generate_include_with_path():
    # Given the generate_include function is called with path=True
    # When the function is executed
    results = generate_include()

    # Then it should return a string that includes "include {" and "path = find_in_parent_folders()"
    assert 'include {\n    path = find_in_parent_folders()\n}\n' in results


def test_generate_include_without_path():
    # Given the generate_include function is called with path=False
    # When the function is executed

    results = generate_include(False)

    # Then it should return a string that includes "include {" and an empty path value.
    assert '' in results


def test_generate_locals():
    # Scenario 1
    # Given the generate_locals function is called with filename="", url="https://gitserver.com/test/test.git", path="modules/test", and version="0.1.0"
    # When the function is executed
    filename = ''
    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'modules/test'
    version: str = '0.1.0'
    results = generate_locals(filename, url, path, version)

    # Then it should return a string that includes the expected "locals" block
    expected = """
locals {
    module = {
        repository = "gitserver.com/test/test.git"
        path = "//modules/test"
        version = "0.1.0"
        source =  "${local.module.repository}${local.module.path != null ? local.module.path : ''}?ref=${local.module.version}"
    }
    environment = get_env("ENV", "development")
    all = merge(
        yamldecode(file(find_in_parent_folders(format("config.%s.yaml", local.environment)))),
    )
}
"""

    assert results == expected


def test_generate_terraform():
    # Scenario 1
    # Given the generate_terraform function is called with url="https://gitserver.com/test/test.git", path="modules/test", version="0.1.0", and lookup="local.all[\"test\"]"
    # When the function is executed
    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'modules/test'
    version: str = '0.1.0'
    lookup: str = 'local.all.test'
    results = generate_terraform(url, path, version, lookup)

    # Then it should return a string that includes the expected "terraform" block
    expected = """
terraform {
    source = lookup(local.all.test, "enabled", true) == true ? local.module.source : null
}
"""

    assert results == expected


def test_generate_inputs():
    # Scenario 1
    # Given the generate_inputs function is called with variables=[{"name": "test", "description": "A", "type": "string", "default": "hello"}] and lookup="local.all[\"test\"]"
    # When the function is executed
    variables: list = [
        {
            'name': 'test',
            'description': 'A',
            'type': 'string',
            'default': 'hello',
        }
    ]
    lookup: str = 'local.all.test'
    results = generate_inputs(variables, lookup)

    # Then it should return a string that includes the expected "inputs" block
    expected = """
inputs = {
    # test - A
    test = lookup(local.all.test, "test", "hello")
}"""
    assert results == expected
