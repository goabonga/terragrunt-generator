from generator.generate import (
    generate,
    generate_header,
    generate_include,
    generate_inputs,
    generate_locals,
    generate_terraform,
    parse_variables,
)


def test_generate_header():
    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'modules/test'
    version: str = '0.1.0'
    lookup: str = 'test'
    name: str = 'test'
    variables = {
        'mandatories': [{'name': 'mandatories', 'description': 'mandatories'}],
        'optionals': [{'name': 'optionals', 'description': 'optionals'}],
        'nullables': [{'name': 'nullables', 'description': 'nullables'}],
    }
    results, yaml = generate_header(name, url, path, version, lookup, variables)

    print(results)

    expected = """# test 0.1.0
# https://gitserver.com/test/test/tree/0.1.0/modules/test
#
# yaml config
# ```
# test:
#   enabled: true
#   # mandatories - mandatories
#   mandatories: 
#   # optionals - optionals
#   # optionals: 
#   # nullables - nullables
#   # nullables: 
# ```
#
"""
    assert results == expected


def test_generate_header_with_deep_lookup():
    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'modules/test'
    version: str = '0.1.0'
    lookup: str = 'app.test'
    name: str = 'test'
    variables = {
        'mandatories': [{'name': 'mandatories', 'description': 'mandatories'}],
        'optionals': [{'name': 'optionals', 'description': 'optionals'}],
        'nullables': [{'name': 'nullables', 'description': 'nullables'}],
    }
    results, yaml = generate_header(name, url, path, version, lookup, variables)

    print(results)

    expected = """# test 0.1.0
# https://gitserver.com/test/test/tree/0.1.0/modules/test
#
# yaml config
# ```
# app:
#   test:
#     enabled: true
#     # mandatories - mandatories
#     mandatories: 
#     # optionals - optionals
#     # optionals: 
#     # nullables - nullables
#     # nullables: 
# ```
#
"""
    assert results == expected


def test_generate_header_local_module():
    url: str = './test/test/'
    path: str = None
    version: str = '0.1.0'
    lookup: str = 'test'
    name: str = 'test'
    variables = {
        'mandatories': [{'name': 'mandatories', 'description': 'mandatories'}],
        'optionals': [{'name': 'optionals', 'description': 'optionals'}],
        'nullables': [{'name': 'nullables', 'description': 'nullables'}],
    }
    results, yaml = generate_header(name, url, path, version, lookup, variables)
    excepted = """# test 0.1.0
# ./test/test/
#
# yaml config
# ```
# test:
#   enabled: true
#   # mandatories - mandatories
#   mandatories: 
#   # optionals - optionals
#   # optionals: 
#   # nullables - nullables
#   # nullables: 
# ```
#
"""
    assert excepted == results


def test_generate_header_module():
    url: str = 'https://gitserver.com/test/test.git'
    path: str = None
    version: str = '0.1.0'
    lookup: str = 'test'
    name: str = 'test'
    variables = {
        'mandatories': [{'name': 'mandatories', 'description': 'mandatories'}],
        'optionals': [{'name': 'optionals', 'description': 'optionals'}],
        'nullables': [{'name': 'nullables', 'description': 'nullables'}],
    }
    results, yaml = generate_header(name, url, path, version, lookup, variables)
    excepted = """# test 0.1.0
# https://gitserver.com/test/test/tree/0.1.0/
#
# yaml config
# ```
# test:
#   enabled: true
#   # mandatories - mandatories
#   mandatories: 
#   # optionals - optionals
#   # optionals: 
#   # nullables - nullables
#   # nullables: 
# ```
#
"""
    assert excepted == results


def test_generate_header_submodule():
    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'modules/test'
    version: str = '0.1.0'
    lookup: str = 'test'
    name: str = 'test'
    variables = {
        'mandatories': [{'name': 'mandatories', 'description': 'mandatories'}],
        'optionals': [{'name': 'optionals', 'description': 'optionals'}],
        'nullables': [{'name': 'nullables', 'description': 'nullables'}],
    }
    results, yaml = generate_header(name, url, path, version, lookup, variables)
    excepted = """# test 0.1.0
# https://gitserver.com/test/test/tree/0.1.0/modules/test
#
# yaml config
# ```
# test:
#   enabled: true
#   # mandatories - mandatories
#   mandatories: 
#   # optionals - optionals
#   # optionals: 
#   # nullables - nullables
#   # nullables: 
# ```
#
"""
    assert excepted == results


def test_generate_header_nested_lookup():
    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'modules/test'
    version: str = '0.1.0'
    lookup: str = 'test.module'
    name: str = 'test'
    variables = {
        'mandatories': [{'name': 'mandatories', 'description': 'mandatories'}],
        'optionals': [{'name': 'optionals', 'description': 'optionals'}],
        'nullables': [{'name': 'nullables', 'description': 'nullables'}],
    }
    results, yaml = generate_header(name, url, path, version, lookup, variables)
    excepted = """# test 0.1.0
# https://gitserver.com/test/test/tree/0.1.0/modules/test
#
# yaml config
# ```
# test:
#   module:
#     enabled: true
#     # mandatories - mandatories
#     mandatories: 
#     # optionals - optionals
#     # optionals: 
#     # nullables - nullables
#     # nullables: 
# ```
#
"""
    assert excepted == results


def test_generate_include_with_path():
    results = generate_include()
    print(results)

    assert 'include {\n    path = find_in_parent_folders()\n}\n' in results


def test_generate_include_without_path():
    results = generate_include(False)

    assert '' in results


def test_generate_locals():
    url: str = 'https://gitserver.com/test/test.git'
    path = None
    version: str = '0.1.0'
    results = generate_locals(url, path, version)
    print(results)

    expected = """
locals {
    source = "gitserver.com/test/test.git?ref=0.1.0"
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}
"""

    assert results == expected

    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'modules/test'
    version: str = '0.1.0'
    results = generate_locals(url, path, version)
    print(results)

    expected = """
locals {
    source = "gitserver.com/test/test.git//modules/test?ref=0.1.0"
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}
"""

    assert results == expected


def test_generate_terraform():
    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'modules/test'
    version: str = '0.1.0'
    lookup: str = 'test'
    results = generate_terraform(url, path, version, lookup)

    expected = """
terraform {
    source = lookup(local.all, "test", false) == false ? null : lookup(local.all.test, "enabled", false) == false ? null : local.source
}
"""

    assert results == expected


def test_generate_inputs():
    variables: list = [
        {
            'name': 'not_mandatory',
            'description': 'not mandatory',
            'mandatory': False,
        },
        {
            'name': 'mandatory',
            'description': 'mandatory',
            'mandatory': True,
        },
        {
            'name': 'mandatory_typed',
            'description': 'mandatory_typed',
            'mandatory': True,
            'type': 'string',
        },
    ]
    lookup: str = 'test'
    results = generate_inputs(variables, lookup)

    expected = """
inputs = {
    # mandatory - mandatory - required
    mandatory = lookup(local.all.test, "mandatory", null)
    # mandatory_typed - mandatory_typed - required
    mandatory_typed = lookup(local.all.test, "mandatory_typed", "")
    # not_mandatory - not mandatory
    not_mandatory = lookup(local.all.test, "not_mandatory", null)
}"""
    assert results == expected

    variables.append(
        {
            'name': 'nullable',
            'description': 'nullable',
            'nullable': True,
        }
    )

    results = generate_inputs(variables, lookup)

    expected = """
inputs = merge({
    # mandatory - mandatory - required
    mandatory = lookup(local.all.test, "mandatory", null)
    # mandatory_typed - mandatory_typed - required
    mandatory_typed = lookup(local.all.test, "mandatory_typed", "")
    # not_mandatory - not mandatory
    not_mandatory = lookup(local.all.test, "not_mandatory", null)
},
  # nullable - nullable
  (lookup(local.all.test, "nullable", null) == null ? {} : { nullable =  lookup(local.all.test, "nullable") })
)"""
    assert results == expected


def test_parse_variables():
    variables: list = [
        {
            0: {
                'name': 'test',
                'description': 'A',
                'type': 'string',
                'default': None,
            },
            1: {
                'name': 'test1',
                'description': 'A',
                'type': 'string',
                'default': 'hello',
            },
            2: {
                'name': 'test2',
                'description': 'A',
                'type': 'string',
            },
        }
    ]

    results = parse_variables(variables)

    expected = (
        [
            {
                'name': 0,
                'description': 'A',
                'type': 'string',
                'default': None,
                'mandatory': False,
                'nullable': True,
            },
            {
                'name': 1,
                'description': 'A',
                'type': 'string',
                'default': 'hello',
                'mandatory': False,
                'nullable': False,
            },
            {
                'name': 2,
                'description': 'A',
                'type': 'string',
                'mandatory': True,
                'nullable': False,
            },
        ],
        {
            'mandatories': [
                {
                    'name': 2,
                    'description': 'A',
                    'type': 'string',
                    'mandatory': True,
                    'nullable': False,
                }
            ],
            'optionals': [
                {
                    'name': 1,
                    'description': 'A',
                    'type': 'string',
                    'default': 'hello',
                    'mandatory': False,
                    'nullable': False,
                }
            ],
            'nullables': [
                {
                    'name': 0,
                    'description': 'A',
                    'type': 'string',
                    'default': None,
                    'mandatory': False,
                    'nullable': True,
                }
            ],
        },
    )

    assert results == expected


def test_generate():
    hcl_files: list
    include: bool = True

    url: str = 'https://gitserver.com/test/test.git'
    path: str = None
    version: str = '0.1.0'
    lookup: str = 'test'
    name: str = 'test'

    hcl_files = {
        'variable': [
            {
                0: {
                    'name': 'test',
                    'description': 'A',
                    'type': 'string',
                    'default': None,
                },
                1: {
                    'name': 'test1',
                    'description': 'A',
                    'type': 'string',
                    'default': 'hello',
                },
                2: {
                    'name': 'test2',
                    'description': 'A',
                    'type': 'string',
                },
            }
        ]
    }

    results, yaml = generate(
        url,
        path,
        version,
        lookup,
        hcl_files,
        include,
        name,
    )

    expected = '''# test 0.1.0
# https://gitserver.com/test/test/tree/0.1.0/
#
# yaml config
# ```
# test:
#   enabled: true
#   # 2 - A
#   2: 
#   # 1 - A
#   # 1: "hello"
#   # 0 - A
#   # 0: 
# ```
#

include {
    path = find_in_parent_folders()
}

locals {
    source = "gitserver.com/test/test.git?ref=0.1.0"
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}

terraform {
    source = lookup(local.all, "test", false) == false ? null : lookup(local.all.test, "enabled", false) == false ? null : local.source
}

inputs = merge({
    # 2 - A - required
    2 = lookup(local.all.test, "2", "")
    # 1 - A
    1 = lookup(local.all.test, "1", "hello")
},
  # 0 - A
  (lookup(local.all.test, "0", null) == null ? {} : { 0 =  lookup(local.all.test, "0") })
)'''
    print(results)
    assert results == expected

    hcl_files: list
    include: bool = True

    url: str = 'test/test_path'
    path: str = None
    version: str = '0.1.0'
    lookup: str = 'test'
    name: str = 'test'

    hcl_files = {
        'variable': [
            {
                0: {
                    'name': 'test',
                    'description': 'A',
                    'type': 'string',
                    'default': None,
                },
                1: {
                    'name': 'test1',
                    'description': 'A',
                    'type': 'string',
                    'default': 'hello',
                },
                2: {
                    'name': 'test2',
                    'description': 'A',
                    'type': 'string',
                },
            }
        ]
    }

    results, yaml = generate(
        url,
        path,
        version,
        lookup,
        hcl_files,
        include,
        name,
    )

    expected = '''# test 0.1.0
# test/test_path
#
# yaml config
# ```
# test:
#   enabled: true
#   # 2 - A
#   2: 
#   # 1 - A
#   # 1: "hello"
#   # 0 - A
#   # 0: 
# ```
#

include {
    path = find_in_parent_folders()
}

locals {
    source = find_in_parent_folders("test/test_path")
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}

terraform {
    source = lookup(local.all, "test", false) == false ? null : lookup(local.all.test, "enabled", false) == false ? null : local.source
}

inputs = merge({
    # 2 - A - required
    2 = lookup(local.all.test, "2", "")
    # 1 - A
    1 = lookup(local.all.test, "1", "hello")
},
  # 0 - A
  (lookup(local.all.test, "0", null) == null ? {} : { 0 =  lookup(local.all.test, "0") })
)'''
    assert results == expected

    hcl_files: list
    include: bool = True

    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'modules/test'
    version: str = '0.1.0'
    lookup: str = 'test'
    name: str = 'test'

    hcl_files = {
        'variable': [
            {
                0: {
                    'name': 'test',
                    'description': 'A',
                    'type': 'string',
                    'default': None,
                },
                1: {
                    'name': 'test1',
                    'description': 'A',
                    'type': 'string',
                    'default': 'hello',
                },
                2: {
                    'name': 'test2',
                    'description': 'A',
                    'type': 'string',
                },
            }
        ]
    }

    results, yaml = generate(
        url,
        path,
        version,
        lookup,
        hcl_files,
        include,
        name,
    )

    print(results)

    expected = '''# test 0.1.0
# https://gitserver.com/test/test/tree/0.1.0/modules/test
#
# yaml config
# ```
# test:
#   enabled: true
#   # 2 - A
#   2: 
#   # 1 - A
#   # 1: "hello"
#   # 0 - A
#   # 0: 
# ```
#

include {
    path = find_in_parent_folders()
}

locals {
    source = "gitserver.com/test/test.git//modules/test?ref=0.1.0"
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}

terraform {
    source = lookup(local.all, "test", false) == false ? null : lookup(local.all.test, "enabled", false) == false ? null : local.source
}

inputs = merge({
    # 2 - A - required
    2 = lookup(local.all.test, "2", "")
    # 1 - A
    1 = lookup(local.all.test, "1", "hello")
},
  # 0 - A
  (lookup(local.all.test, "0", null) == null ? {} : { 0 =  lookup(local.all.test, "0") })
)'''
    assert results == expected

    hcl_files: list
    include: bool = True

    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'modules/test'
    version: str = '0.1.0'
    lookup: str = 'test'
    name: str = 'test'

    hcl_files = {
        'variable': [
            {
                0: {
                    'name': 'test',
                    'description': 'A',
                    'type': 'string',
                    'default': None,
                },
                1: {
                    'name': 'test1',
                    'description': 'A',
                    'type': 'string',
                    'default': 'hello',
                },
                2: {
                    'name': 'test2',
                    'description': 'A',
                    'type': 'string',
                },
            }
        ]
    }

    results, yaml = generate(
        url,
        path,
        version,
        lookup,
        hcl_files,
        include,
        None,
    )

    print(results)

    expected = '''# test 0.1.0
# https://gitserver.com/test/test/tree/0.1.0/modules/test
#
# yaml config
# ```
# test:
#   enabled: true
#   # 2 - A
#   2: 
#   # 1 - A
#   # 1: "hello"
#   # 0 - A
#   # 0: 
# ```
#

include {
    path = find_in_parent_folders()
}

locals {
    source = "gitserver.com/test/test.git//modules/test?ref=0.1.0"
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}

terraform {
    source = lookup(local.all, "test", false) == false ? null : lookup(local.all.test, "enabled", false) == false ? null : local.source
}

inputs = merge({
    # 2 - A - required
    2 = lookup(local.all.test, "2", "")
    # 1 - A
    1 = lookup(local.all.test, "1", "hello")
},
  # 0 - A
  (lookup(local.all.test, "0", null) == null ? {} : { 0 =  lookup(local.all.test, "0") })
)'''
    assert results == expected
