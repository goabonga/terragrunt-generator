import json


def generate_header(
    name: str, version: str, lookup: str, variables: list = []
) -> str:
    text: str = ''

    # for variable_values in variables:
    for variable in variables.get('mandatories'):
        default = variable.get('default', None)
        text += (
            f"#   {variable['name']}:"
            f" {json.dumps(default) if default is not None else ''}\n"
        )
    for variable in variables.get('optionals'):
        default = variable.get('default', None)
        text += (
            f"#   {variable['name']}:"
            f" {json.dumps(default) if default is not None else ''}\n"
        )
    for variable in variables.get('nullables'):
        default = variable.get('default', None)
        text += (
            f"#   # {variable['name']}:"
            f" {json.dumps(default) if default is not None else ''}\n"
        )

    lookup = lookup.replace('local.all', '')
    if lookup.startswith('['):
        lookup = lookup.replace('[', '').replace(']', '').replace('"', '')

    return f"""# {name} {version}
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
        content = '    path = "${find_in_parent_folders()}"'
    return f"""include {{
{content}
}}
"""


def generate_locals(filename: str = 'config.yaml') -> str:
    filename = (
        f"{filename.removeprefix('#')}"
        if filename.startswith('#') is True
        else f'"{filename}"'
    )
    return f"""
locals {{
    all = merge(
        yamldecode(file({filename})),
    )
}}
"""


def generate_terraform(url: str, path: str, version: str, lookup: str) -> str:
    path = f'//{path}' if path is not None else ''
    url = f'{url}{path}?ref={version}'
    source = f'lookup({lookup}, "enabled", true) == true ? "{url}" : null'
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
            .replace('    ', '', 1)
            .replace('\n', '\n    #')
            .replace('\\"', '"')
        )
        if variable.get('nullable', False) is False:
            _content: str = ''
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
            content_nullable += f'{{ {name} =  lookup({lookup}, "{name}") }}'
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


def parse_variables(variables: list) -> list:
    """
    this function parse raw hcl variables and produce a clear objects list

    Args:
        variables (list): the raw hcl variables list

    Returns:
        list: the variables object list
    """
    outputs: list = []

    mandatories: list = []
    optionals: list = []
    nullables: list = []

    #   def set_name(variable: dict, name: str) -> dict:
    #       return variable
    #
    #   def set_type(variable: dict) -> dict:
    #       return variable
    #
    #   def is_mandatory(variable: dict) -> dict:
    #       return variable
    #
    #   def is_nullable(variable: dict) -> dict:
    #       return variable

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
    hcl_files: list,
    include: bool = True,
    config: str = 'config.yaml',
    lookup: str = '["{name}"]',
    name: str = None,
) -> str:
    # parse variables
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

    lookup = f'local.all{lookup.format(name=name,)}'
    results: str
    results = generate_header(name, version, lookup, variables_object)
    results += generate_include(include)
    results += generate_locals(config)
    results += generate_terraform(url, path, version, lookup)
    results += generate_inputs(variables, lookup)
    return results
