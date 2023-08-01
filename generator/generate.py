import json


def generate_header(
    name: str,
    url: str,
    path: str,
    version: str,
    lookup: str,
    variables: list = [],
) -> str:
    text = ''

    for var_type in ('mandatories', 'optionals', 'nullables'):
        for variable in variables.get(var_type, []):
            default = variable.get('default')
            description = (
                variable.get('description', '')
                .replace('    ', '', 1)
                .replace('\n', '\n#   #')
                .replace('\\"', '"')
            )
            text += f"#   # {variable['name']} - {description}\n"
            if var_type == 'nullables':
                text += f"#   # {variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"
            else:
                text += f"#   {variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"

    lookup = lookup.replace('local.all', '')
    path = path or ''
    url = f"{url.replace('.git', '')}/tree/{version}/{path}"

    return f"""# {name} {version}
# {url}
#
# yaml config
# ```
# {lookup}:
#   enabled: true
{text}# ```
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
    module = {{
        repository = "{url.replace("https://", "").replace("http://", "")}"
        path = {f'"//{path}"' if path != None else "null"}
        version = "{version}"
        source =  "${{local.module.repository}}${{local.module.path != null ? local.module.path : \'\'}}?ref=${{local.module.version}}"
    }}
    environment = get_env("CONFIG", "test")
    all = merge(
        yamldecode(file(find_in_parent_folders(format("config.%s.yaml", local.environment)))),
    )
}}
"""


def generate_terraform(url: str, path: str, version: str, lookup: str) -> str:
    path = f'//{path}' if path is not None else ''
    url = f'{url.replace("https://", "").replace("http://", "")}{path}?ref={version}'

    source = f'lookup(local.all.{lookup}, "enabled", true) == true ? local.module.source : null'

    return f"""
terraform {{
    source = {source}
}}
"""


def generate_inputs(variables: list = [], lookup: str = 'local.all') -> str:
    content_fisrt: str = ''
    content_next: str = ''
    content_nullable: str = ''
    variables = sorted(variables, key=lambda d: d['name'], reverse=False)

    for variable in variables:
        description = (
            variable.get('description', '')
            .replace('    ', '')
            .replace('\n', '\n    # ')
            .replace('\\"', '"')
        )

        if variable.get('nullable', False) is False:
            _content: str = ''

            line_doc = f"{variable.get('name')} - {description}"
            mandatory = variable.get('mandatory', False)
            line_doc += ' - required' if mandatory is True else ''

            line_content = f"{variable.get('name')} = "
            name = variable.get('name')

            line_content += f'lookup(local.all.{lookup}, "{name}"'

            value = ''
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
            name = variable.get('name')
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
            # reformat variable type
            if v.get('type', None) is not None:
                v['type'] = v['type'].replace('${', '').replace('}', '')
            # define if is mandatory or nullable

            if 'default' not in list(v.keys()):
                v['mandatory'] = True
                v['nullable'] = False
            elif 'default' in list(v.keys()) and v.get('default', '') is None:
                v['mandatory'] = False
                v['nullable'] = True
            else:
                v['mandatory'] = False
                v['nullable'] = False
            # set name
            v = v | {'name': k}
            # add object to outputs
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

    name = (
        (
            path.split('/')[-1:][0]
            if path is not None
            else url.split('/')[-1:][0].replace('.git', '')
        )
        if name is None
        else name
    )

    # lookup = f'local.all{lookup.format(name=name,)}'
    results: str
    results = generate_header(name, url, path, version, lookup, variables_object)
    results += generate_include(include)
    results += generate_locals(url, path, version)
    results += generate_terraform(url, path, version, lookup)
    results += generate_inputs(variables, lookup)
    return results
