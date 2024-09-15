import json
import os

from generator.yaml import get_yaml


def generate_header(
    name: str,
    url: str,
    path: str,
    version: str,
    lookup: str,
    variables: map = {
        'mandatories': {},
        'optionals': {},
        'nullables': {},
    },
) -> str:
    lookup = lookup.replace('local.all', '')
    path = path or ''
    if 'http' in url:
        url = f"{url.replace('.git', '')}/tree/{version}/{path}"

    # Check if lookup can be split and if it has at least one part after splitting
    lookup_parts = lookup.split('.')
    if len(lookup_parts) > 1:
        lookup_prefix = lookup_parts[:-1][0]
    else:
        lookup_prefix = lookup  # Use lookup directly if it cannot be split

    yaml = (
        get_yaml(lookup, variables)
        .replace(f'{lookup_prefix}:', f'# {lookup_prefix}:')
        .replace('\n  ', '\n#   ')
    )

    return f"""# {name} {version}
# {url}
#
# yaml config
# ```
{yaml}# ```
#
"""


def generate_include(enable: bool = True) -> str:
    content: str = ''
    if enable is True:
        content = '    path = find_in_parent_folders()'
        return f"""
include {{
{content}
}}
"""
    return ''


def generate_locals(
    url: str = None,
    path: str = None,
    version: str = None,
) -> str:
    return f"""
locals {{
    source = {
        f'"{url.replace("https://", "").replace("http://", "")}{f"//{path}" if path != None else ""}?ref={version}"' if "http" in url else f'find_in_parent_folders("{url}")'
    }
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}}
"""


def generate_terraform(url: str, path: str, version: str, lookup: str) -> str:
    lookups = lookup.split('.')
    previous = "local.all"
    source = ""
    for lookups_item in lookups:
        source += f'lookup({previous}, "{lookups_item}", false) == false ? null : '
        previous = f"{previous}.{lookups_item}"
    source += f'lookup({previous}, "enabled", false) == false ? null : local.source'

    path = f'//{path}' if path is not None else ''
    url = f'{url.replace("https://", "").replace("http://", "")}{path}?ref={version}'
    # source = (
    #     f'lookup(local.all.{lookup}, "enabled", true) == true ? local.source : null'
    # )
    return f"""
terraform {{
    source = {source}
}}
"""


# f'lookup(local.all.{lookup}, "enabled", true) == true ? local.source : null'


def generate_inputs(variables: list = [], lookup: str = 'local.all') -> str:
    content_fisrt: str = ''
    content_next: str = ''
    content_nullable: str = ''
    variables: list = sorted(variables, key=lambda d: d['name'], reverse=False)
    for variable in variables:
        description = (
            variable.get('description', '')
            .replace('    ', '')
            .replace('\n', '\n    # ')
            .replace('\\"', '"')
        )
        if variable.get('nullable', False) is False:
            _content: str = ''
            line_doc: str = f"{variable.get('name')} - {description}"
            mandatory = variable.get('mandatory', False)
            line_doc += ' - required' if mandatory is True else ''
            line_content: str = f"{variable.get('name')} = "
            name = variable.get('name')
            line_content += f'lookup(local.all.{lookup}, "{name}"'
            value: str = ''
            if variable.get('type', None) == 'string':
                value = f', "{variable.get("default", "")}"'
            else:
                value = f', {json.dumps(variable.get("default"))}'
            line_content += value
            line_content += ')'
            _content = f"""    # {line_doc}
    {line_content}
"""
            if variable.get('mandatory', False) is True:
                content_fisrt += _content
            else:
                content_next += _content
        else:
            name: str = variable.get('name')
            content_nullable += f'\n  # {name} - {description}'
            content_nullable += f'\n  (lookup(local.all.{lookup}, "{name}", null)'
            content_nullable += ' == null ? {} : '
            content_nullable += f'{{ {name} =  lookup(local.all.{lookup}, "{name}") }}'
            content_nullable += '),'

    if content_nullable != '':
        return f"""
inputs = merge({{
{content_fisrt}{content_next.rstrip(content_next[-1])}
}},{content_nullable.rstrip(content_nullable[-1])}
)"""

    return f"""
inputs = {{
{content_fisrt}{content_next.rstrip(content_next[-1])}
}}"""


def parse_variables(variables: list) -> list:
    outputs: list = []
    mandatories: list = []
    optionals: list = []
    nullables: list = []
    for variable in variables:
        for k in variable:
            v: dict = variable[k].copy()
            if v.get('type', None) is not None:
                v['type'] = v['type'].replace('${', '').replace('}', '')
            if 'default' not in list(v.keys()):
                v['mandatory'] = True
                v['nullable'] = False
            elif 'default' in list(v.keys()) and v.get('default', '') is None:
                v['mandatory'] = False
                v['nullable'] = True
            else:
                v['mandatory'] = False
                v['nullable'] = False
            v = v | {'name': k}
            if v.get('mandatory') is True:
                mandatories.append(v)
            if v.get('nullable') is True:
                nullables.append(v)
            if v.get('mandatory') is False and v.get('nullable') is False:
                optionals.append(v)
            outputs.append(v)
    return outputs, {
        'mandatories': mandatories,
        'optionals': optionals,
        'nullables': nullables,
    }


def generate(
    url: str,
    path: str,
    version: str,
    lookup: str,
    hcl_files: list,
    include: bool = True,
    name: str = None,
) -> str:
    variables, variables_object = parse_variables(hcl_files['variable'])

    if name is None:
        if path is not None:
            name = path.split('/')[-1:][0]
        else:
            name = os.path.dirname(url).split('/')[-1:][0].replace('.git', '')

    results: str
    results = generate_header(name, url, path, version, lookup, variables_object)
    results += generate_include(include)
    results += generate_locals(url, path, version)
    results += generate_terraform(url, path, version, lookup)
    results += generate_inputs(variables, lookup)
    return results
