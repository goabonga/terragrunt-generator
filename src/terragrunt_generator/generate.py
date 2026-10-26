# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import json
from collections.abc import Callable, Sequence
from typing import Any

from terragrunt_generator.source import ModuleSource, module_source
from terragrunt_generator.variables import (
    Variable,
    VariableKind,
    parse_variables,
)
from terragrunt_generator.yaml import get_yaml


def generate_header(
    name: str,
    source: ModuleSource,
    lookup: str,
    variables: Sequence[Variable] = (),
    enabled: bool = True,
) -> tuple[str, str]:
    lookup = lookup.replace("local.all", "")

    lookup_prefix = lookup.split(".")[0]

    yaml_raw = get_yaml(lookup, variables, enabled)
    yaml_comment = yaml_raw.replace(f"{lookup_prefix}:", f"# {lookup_prefix}:").replace(
        "\n  ", "\n#   "
    )

    header = f"""# {name} {source.version}
# {source.web_url}
#
# yaml config
# ```
{yaml_comment}# ```
#
"""
    return header, yaml_raw


def generate_include(enable: bool = True) -> str:
    if enable is not True:
        return ""
    return """
include {
    path = find_in_parent_folders()
}
"""


def generate_locals(
    source: ModuleSource,
    config_filename: str = "config.yaml",
    yaml_env: str | None = None,
) -> str:
    config_line = (
        'format("config.%s.yaml", local.environment)'
        if yaml_env
        else f'"{config_filename}"'
    )

    env_line = f'environment = get_env("ENV", "{yaml_env}")\n    ' if yaml_env else ""

    return f"""
locals {{
    {env_line}source = {source.terragrunt_source}
    all = merge(
        yamldecode(file(find_in_parent_folders({config_line}))),
    )
}}
"""


def generate_terraform(lookup: str) -> str:
    """The source of the module, unless the lookup or its ``enabled`` is missing or false."""
    scope = "local.all"
    guards = ""
    for key in [*lookup.split("."), "enabled"]:
        guards += f'lookup({scope}, "{key}", false) == false ? null : '
        scope = f"{scope}.{key}"

    return f"""
terraform {{
    source = {guards}local.source
}}
"""


def input_description(variable: Variable) -> str:
    return (
        variable.description.replace("    ", "")
        .replace("\n", "\n    # ")
        .replace('\\"', '"')
    )


def render_input(variable: Variable, lookup: str) -> str:
    """The documented ``lookup`` line of a mandatory or optional variable."""
    doc = f"{variable.name} - {input_description(variable)}"
    if variable.kind is VariableKind.MANDATORY:
        doc += " - required"
    if variable.type == "string":
        text = "" if variable.value is None else variable.value
        default = f', "{text}"'
    else:
        default = f", {json.dumps(variable.value)}"
    return (
        f"    # {doc}\n"
        f'    {variable.name} = lookup(local.all.{lookup}, "{variable.name}"{default})\n'
    )


def render_nullable(variable: Variable, lookup: str) -> str:
    """The merge entry of a variable that defaults to null."""
    name = variable.name
    return (
        f"\n  # {name} - {input_description(variable)}"
        f'\n  (lookup(local.all.{lookup}, "{name}", null)'
        " == null ? {} : "
        f'{{ {name} =  lookup(local.all.{lookup}, "{name}") }}'
        "),"
    )


def generate_inputs(
    variables: Sequence[Variable] = (), lookup: str = "local.all"
) -> str:
    ordered = sorted(variables, key=lambda variable: variable.name)

    def rendered(kind: VariableKind, render: Callable[[Variable, str], str]) -> str:
        return "".join(render(v, lookup) for v in ordered if v.kind is kind)

    mandatory = rendered(VariableKind.MANDATORY, render_input)
    optional = rendered(VariableKind.OPTIONAL, render_input).rstrip("\n")
    nullable = rendered(VariableKind.NULLABLE, render_nullable).rstrip(",")

    if nullable != "":
        return f"""
inputs = merge({{
{mandatory}{optional}
}},{nullable}
)"""

    return f"""
inputs = {{
{mandatory}{optional}
}}"""


def generate(
    url: str,
    path: str | None,
    version: str,
    lookup: str,
    hcl_files: dict[str, Any],
    include: bool = True,
    name: str | None = None,
    config_filename: str = "config.yaml",
    yaml_env: str | None = None,
    enabled: bool = True,
) -> tuple[str, str]:
    variables = parse_variables(hcl_files.get("variable", []))
    source = module_source(url, version, path)

    header, yaml = generate_header(
        source.name if name is None else name, source, lookup, variables, enabled
    )
    sections = [
        header,
        generate_include(include),
        generate_locals(source, config_filename, yaml_env),
        generate_terraform(lookup),
        generate_inputs(variables, lookup),
    ]

    return "".join(sections), yaml
