# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

from terragrunt_generator.generate import (
    generate,
    generate_header,
    generate_include,
    generate_inputs,
    generate_locals,
    generate_terraform,
)
from terragrunt_generator.source import GitSource
from terragrunt_generator.variables import Variable


def test_generate_header():
    url: str = "https://gitserver.com/test/test.git"
    path: str = "modules/test"
    version: str = "0.1.0"
    lookup: str = "test"
    name: str = "test"
    variables = [
        Variable("mandatories", "mandatories"),
        Variable("optionals", "optionals", default=""),
        Variable("nullables", "nullables", default=None),
    ]
    results, yaml = generate_header(
        name, GitSource(url, version, path), lookup, variables
    )

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


def test_generate_header_default_variables():
    # Omitting `variables` documents a module without any variable.
    results, yaml = generate_header(
        name="test",
        source=GitSource("https://gitserver.com/test/test.git", "0.1.0"),
        lookup="test",
    )
    assert "# test 0.1.0" in results
    assert "enabled: true" in yaml


def test_generate_header_with_deep_lookup():
    url: str = "https://gitserver.com/test/test.git"
    path: str = "modules/test"
    version: str = "0.1.0"
    lookup: str = "app.test"
    name: str = "test"
    variables = [
        Variable("mandatories", "mandatories"),
        Variable("optionals", "optionals", default=""),
        Variable("nullables", "nullables", default=None),
    ]
    results, yaml = generate_header(
        name, GitSource(url, version, path), lookup, variables
    )

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
    url: str = "./test/test/"
    path: str = None
    version: str = "0.1.0"
    lookup: str = "test"
    name: str = "test"
    variables = [
        Variable("mandatories", "mandatories"),
        Variable("optionals", "optionals", default=""),
        Variable("nullables", "nullables", default=None),
    ]
    results, yaml = generate_header(
        name, GitSource(url, version, path), lookup, variables
    )
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
    url: str = "https://gitserver.com/test/test.git"
    path: str = None
    version: str = "0.1.0"
    lookup: str = "test"
    name: str = "test"
    variables = [
        Variable("mandatories", "mandatories"),
        Variable("optionals", "optionals", default=""),
        Variable("nullables", "nullables", default=None),
    ]
    results, yaml = generate_header(
        name, GitSource(url, version, path), lookup, variables
    )
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
    url: str = "https://gitserver.com/test/test.git"
    path: str = "modules/test"
    version: str = "0.1.0"
    lookup: str = "test"
    name: str = "test"
    variables = [
        Variable("mandatories", "mandatories"),
        Variable("optionals", "optionals", default=""),
        Variable("nullables", "nullables", default=None),
    ]
    results, yaml = generate_header(
        name, GitSource(url, version, path), lookup, variables
    )
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
    url: str = "https://gitserver.com/test/test.git"
    path: str = "modules/test"
    version: str = "0.1.0"
    lookup: str = "test.module"
    name: str = "test"
    variables = [
        Variable("mandatories", "mandatories"),
        Variable("optionals", "optionals", default=""),
        Variable("nullables", "nullables", default=None),
    ]
    results, yaml = generate_header(
        name, GitSource(url, version, path), lookup, variables
    )
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

    assert "include {\n    path = find_in_parent_folders()\n}\n" in results


def test_generate_include_without_path():
    results = generate_include(False)

    assert "" in results


def test_generate_locals():
    url: str = "https://gitserver.com/test/test.git"
    path = None
    version: str = "0.1.0"
    results = generate_locals(GitSource(url, version, path))
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

    url: str = "https://gitserver.com/test/test.git"
    path: str = "modules/test"
    version: str = "0.1.0"
    results = generate_locals(GitSource(url, version, path))
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
    lookup: str = "test"
    results = generate_terraform(lookup)

    expected = """
terraform {
    source = lookup(local.all, "test", false) == false ? null : lookup(local.all.test, "enabled", false) == false ? null : local.source
}
"""

    assert results == expected


def test_generate_inputs():
    variables: list[Variable] = [
        Variable("not_mandatory", "not mandatory", default="value"),
        Variable("mandatory", "mandatory"),
        Variable("mandatory_typed", "mandatory_typed", type="string"),
    ]
    lookup: str = "test"
    results = generate_inputs(variables, lookup)

    expected = """
inputs = {
    # mandatory - mandatory - required
    mandatory = lookup(local.all.test, "mandatory", null)
    # mandatory_typed - mandatory_typed - required
    mandatory_typed = lookup(local.all.test, "mandatory_typed", "")
    # not_mandatory - not mandatory
    not_mandatory = lookup(local.all.test, "not_mandatory", "value")
}"""
    assert results == expected

    variables.append(Variable("nullable", "nullable", default=None))

    results = generate_inputs(variables, lookup)

    expected = """
inputs = merge({
    # mandatory - mandatory - required
    mandatory = lookup(local.all.test, "mandatory", null)
    # mandatory_typed - mandatory_typed - required
    mandatory_typed = lookup(local.all.test, "mandatory_typed", "")
    # not_mandatory - not mandatory
    not_mandatory = lookup(local.all.test, "not_mandatory", "value")
},
  # nullable - nullable
  (lookup(local.all.test, "nullable", null) == null ? {} : { nullable =  lookup(local.all.test, "nullable") })
)"""
    assert results == expected


def test_generate_inputs_without_optional_merge_branch():
    # Regression: a module whose variables are only mandatory and nullable
    # has no optional input. The merge({...}) branch must still render.
    variables = [
        Variable("mandatory", "mandatory"),
        Variable("znullable", "nullable", default=None),
    ]
    results = generate_inputs(variables, "test")

    assert "inputs = merge({" in results
    assert 'mandatory = lookup(local.all.test, "mandatory", null)' in results
    assert "znullable" in results


def test_generate_inputs_only_mandatory_plain_branch():
    # Regression: only-mandatory variables leave both the optional and the
    # nullable inputs empty, which must render the plain inputs = {...} branch.
    variables = [Variable("mandatory", "mandatory")]
    results = generate_inputs(variables, "test")

    assert results.startswith("\ninputs = {")
    assert 'mandatory = lookup(local.all.test, "mandatory", null)' in results


def test_generate_inputs_renders_typed_and_untyped_defaults():
    variables = [
        Variable("count", "count", type="number", default=3),
        Variable("name", "name", type="string", default="web"),
        Variable("tags", "tags", default={"env": "dev"}),
    ]
    results = generate_inputs(variables, "test")

    assert 'count = lookup(local.all.test, "count", 3)' in results
    assert 'name = lookup(local.all.test, "name", "web")' in results
    assert 'tags = lookup(local.all.test, "tags", {"env": "dev"})' in results


def test_generate_inputs_flattens_multiline_descriptions():
    variables = [Variable("a", 'first\n    second \\"quoted\\"')]
    results = generate_inputs(variables, "test")

    assert '# a - first\n    # second "quoted" - required\n' in results


def test_generate_without_variable_key():
    # Regression: a module that contributes no `variable` blocks leaves
    # hcl_files without a "variable" key. generate must not raise KeyError.
    results, yaml = generate(
        url="https://gitserver.com/test/test.git",
        path=None,
        version="0.1.0",
        lookup="test",
        hcl_files={},
        include=True,
        name="test",
    )

    assert "inputs = {" in results
    assert "enabled: true" in yaml


def test_generate():
    hcl_files: list
    include: bool = True

    url: str = "https://gitserver.com/test/test.git"
    path: str = None
    version: str = "0.1.0"
    lookup: str = "test"
    name: str = "test"

    hcl_files = {
        "variable": [
            {
                0: {
                    "name": "test",
                    "description": "A",
                    "type": "string",
                    "default": None,
                },
                1: {
                    "name": "test1",
                    "description": "A",
                    "type": "string",
                    "default": "hello",
                },
                2: {
                    "name": "test2",
                    "description": "A",
                    "type": "string",
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

    expected = """# test 0.1.0
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
)"""
    print(results)
    assert results == expected

    hcl_files: list
    include: bool = True

    url: str = "test/test_path"
    path: str = None
    version: str = "0.1.0"
    lookup: str = "test"
    name: str = "test"

    hcl_files = {
        "variable": [
            {
                0: {
                    "name": "test",
                    "description": "A",
                    "type": "string",
                    "default": None,
                },
                1: {
                    "name": "test1",
                    "description": "A",
                    "type": "string",
                    "default": "hello",
                },
                2: {
                    "name": "test2",
                    "description": "A",
                    "type": "string",
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

    expected = """# test 0.1.0
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
)"""
    assert results == expected

    hcl_files: list
    include: bool = True

    url: str = "https://gitserver.com/test/test.git"
    path: str = "modules/test"
    version: str = "0.1.0"
    lookup: str = "test"
    name: str = "test"

    hcl_files = {
        "variable": [
            {
                0: {
                    "name": "test",
                    "description": "A",
                    "type": "string",
                    "default": None,
                },
                1: {
                    "name": "test1",
                    "description": "A",
                    "type": "string",
                    "default": "hello",
                },
                2: {
                    "name": "test2",
                    "description": "A",
                    "type": "string",
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

    expected = """# test 0.1.0
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
)"""
    assert results == expected

    hcl_files: list
    include: bool = True

    url: str = "https://gitserver.com/test/test.git"
    path: str = "modules/test"
    version: str = "0.1.0"
    lookup: str = "test"
    name: str = "test"

    hcl_files = {
        "variable": [
            {
                0: {
                    "name": "test",
                    "description": "A",
                    "type": "string",
                    "default": None,
                },
                1: {
                    "name": "test1",
                    "description": "A",
                    "type": "string",
                    "default": "hello",
                },
                2: {
                    "name": "test2",
                    "description": "A",
                    "type": "string",
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

    expected = """# test 0.1.0
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
)"""
    assert results == expected
