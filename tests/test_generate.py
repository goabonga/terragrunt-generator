from generator.generate import (generate, generate_include, generate_inputs,
                                generate_locals, generate_terraform)


def test_generate_include():
    results = generate_include()
    assert (
        'include {\n    path = "${{find_in_parent_folders()}}"\n}\n'
        in results
    )


def test_generate_locals():
    results = generate_locals()
    assert (
        '\nlocals {\n    all = merge(\n        yamldecode(file('
        + 'find_in_parent_folders("config.yaml"))),\n    )\n}\n'
        in results
    )


def test_generate_terraform():
    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'moudles/test'
    version: str = '0.1.0'
    lookup: str = 'local.all["test"]'
    results = generate_terraform(url, path, version, lookup)
    assert (
        results
        == '\nterraform {\n    source = lookup(local.all["test"],'
        + ' "enabled", true) == true ? "https://gitserver.com/test/'
        + 'test.git//moudles/test?ref=0.1.0" : null\n}\n'
    )


def test_generate_inputs():
    variables: list = [
        {
            'name': 'test',
            'description': 'A',
            'type': 'string',
            'default': 'hello',
        }
    ]
    lookup: str = 'local.all["test"]'
    results = generate_inputs(variables, lookup)
    assert (
        results
        == '\ninputs = {\n    # test - A\n    test = '
        + 'lookup(local.all["test"], "test", "hello")\n\n}\n'
    )


def test_generate():
    variables = {'variable': [{'test': {'default': '', 'type': 'string'}}]}
    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'moudles/test'
    version: str = '0.1.0'
    results: str = generate(url, path, version, variables=variables)
    assert f'{url}//{path}?ref={version}' in results
    assert 'lookup(local.all["test"], "test", ' in results
