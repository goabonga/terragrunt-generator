# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import json
import os
from collections.abc import Callable, Sequence
from typing import Any

from terragrunt_generator.variables import (
    Variable,
    VariableKind,
    parse_variables,
)
from terragrunt_generator.yaml import get_yaml


def generate_header(
    name: str,
    url: str,
    path: str | None,
    version: str,
    lookup: str,
    variables: Sequence[Variable] = (),
    enabled: bool = True,
) -> tuple[str, str]:
    lookup = lookup.replace("local.all", "")
    path = path or ""
    if "http" in url:
        url = f"{url.replace('.git', '')}/tree/{version}/{path}"

    lookup_parts = lookup.split(".")
    lookup_prefix = lookup_parts[:-1][0] if len(lookup_parts) > 1 else lookup

    yaml_raw = get_yaml(lookup, variables, enabled)
    yaml_comment = yaml_raw.replace(f"{lookup_prefix}:", f"# {lookup_prefix}:").replace(
        "\n  ", "\n#   "
    )

    header = f"""# {name} {version}
# {url}
#
# yaml config
# ```
{yaml_comment}# ```
#
"""
    return header, yaml_raw


def generate_include(enable: bool = True) -> str:
    content: str = ""
    if enable is True:
        content = "    path = find_in_parent_folders()"
        return f"""
include {{
{content}
}}
"""
    return ""


def generate_locals(
    url: str,
    path: str | None = None,
    version: str = "",
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
    {env_line}source = {
        f'"{url.replace("https://", "").replace("http://", "")}{f"//{path}" if path is not None else ""}?ref={version}"'
        if "http" in url
        else f'find_in_parent_folders("{url}")'
    }
    all = merge(
        yamldecode(file(find_in_parent_folders({config_line}))),
    )
}}
"""


def generate_terraform(url: str, path: str | None, version: str, lookup: str) -> str:
    lookups = lookup.split(".")
    previous = "local.all"
    source = ""
    for lookups_item in lookups:
        source += f'lookup({previous}, "{lookups_item}", false) == false ? null : '
        previous = f"{previous}.{lookups_item}"
    source += f'lookup({previous}, "enabled", false) == false ? null : local.source'

    path = f"//{path}" if path is not None else ""
    url = f"{url.replace('https://', '').replace('http://', '')}{path}?ref={version}"

    return f"""
terraform {{
    source = {source}
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

    if name is None:
        if path is not None:
            name = path.split("/")[-1:][0]
        else:
            name = os.path.dirname(url).split("/")[-1:][0].replace(".git", "")

    header, yaml = generate_header(name, url, path, version, lookup, variables, enabled)
    results: str
    results = header
    results += generate_include(include)
    results += generate_locals(url, path, version, config_filename, yaml_env)
    results += generate_terraform(url, path, version, lookup)
    results += generate_inputs(variables, lookup)

    return results, yaml
