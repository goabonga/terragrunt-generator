import json


def generate_header(name: str, version: str, variables: list = []) -> str:
    text: str = ''
    for variable in variables:
        default = variable.get('default', None)
        text += (
            f"#   {variable['name']}:"
            f" {json.dumps(default) if default is not None else ''}\n"
        )

    return f"""# {name} {version}
#
# yaml config
# ```
# {name}:
#   enabled: true
{text}# ```
#
"""


def generate_include(enable: bool = True) -> str:
    content: str = ''
    if enable is True:
        content = "    path = \"${find_in_parent_folders()}\""
    return f"""include {{
{content}
}}
"""


def generate_locals(filename: str = 'config.yaml') -> str:
    filename = f"{filename.removeprefix('#')}" \
        if filename.startswith('#') is True else f'"{filename}"'
    return f"""
locals {{
    all = merge(
        yamldecode(file({filename})),
    )
}}
"""


def generate_terraform(
    url: str, path: str, version: str, lookup: str
) -> str:
    path = f'//{path}' if path is not None else ''
    url = f'{url}{path}?ref={version}'
    source = f'lookup({lookup}, "enabled", true) == true ? "{url}" : null'
    return f"""
terraform {{
    source = {source}
}}
"""


def generate_inputs(
    variables: list = [], lookup: str = 'local.all'
) -> str:
    content_fisrt: str = ''
    content_next: str = ''
    content_nullable: str = ''
    variables = sorted(variables, key=lambda d: d['name'], reverse=False)
    for variable in variables:
        if variable.get('nullable', False) is False:
            _content: str = ''
            description = (
                variable.get('description', '')
                .replace('    ', '', 1)
                .replace('\n', '\n    #')
                .replace('\\"', '"')
            )
            line_doc = f"{variable.get('name')} - {description}"
            mandatory = variable.get('mandatory', False)
            line_doc += ' - required' if mandatory is True else ''

            line_content = f"{variable.get('name')} = "
            name = variable.get('name')
            line_content += f'lookup({lookup}, "{name}"'

            value = ''
            if variable.get('type', None) == 'string':
                value = f', "{variable.get("default")}"'
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
            name = variable.get('name')
            content_nullable += f'\n  # {name} - {description}'
            content_nullable += f'\n  (lookup({lookup}, "{name}", null)'
            content_nullable += ' == null ? {} : '
            content_nullable += (
                f'{{ {name} =  lookup({lookup}, "{name}") }}'
            )
            content_nullable += '),'

    if content_nullable != '':

        return f"""
inputs = merge({{
{content_fisrt}{content_next}
}},{content_nullable.rstrip(content_nullable[-1])}
)
"""

    return f"""
inputs = {{
{content_fisrt}{content_next}
}}
"""


def generate(url: str, path: str, version: str, variables: list,
             include: bool = True, config: str = 'config.yaml',
             lookup: str = "[\"{name}\"]") -> str:

    _variables: list = []

    for variable in variables['variable']:
        for k in variable:
            v: dict = variable[k].copy()

            if v.get('type', None) is not None:
                v['type'] = v['type'].replace('${', '').replace('}', '')

            if 'default' not in list(v.keys()):
                v['mandatory'] = True
                v['nullable'] = False
            elif (
                'default' in list(v.keys())
                and v.get('default', '') is None
            ):
                v['mandatory'] = False
                v['nullable'] = True
            else:
                v['mandatory'] = False
                v['nullable'] = False

            v = v | {'name': k}

            _variables.append(v)
    variables = _variables

    name = (
        path.split('/')[-1:][0]
        if path is not None
        else url.split('/')[-1:][0].replace('.git', '')
    )
    lookup = f'local.all{lookup.format(name=name,)}'
    results: str
    results = generate_header(name, version, variables)
    results += generate_include(include)
    results += generate_locals(config)
    results += generate_terraform(
        url, path, version, lookup
    )
    results += generate_inputs(variables, lookup)
    return results
