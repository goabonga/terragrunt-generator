import json


def get_yaml(name: str, variables) -> str:
    text: str = ''
    for var_type in ('mandatories', 'optionals', 'nullables'):
        for variable in variables.get(var_type, []):
            default = variable.get('default')
            description = (
                variable.get('description', '')
                .replace('    ', '', 1)
                .replace('\n', '\n#   #')
                .replace('\\"', '"')
            )
            text += f"  # {variable['name']} - {description}\n"
            if var_type == 'nullables':
                text += f"  # {variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"
            elif var_type == 'optionals':
                text += f"  # {variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"
            else:
                text += f"  {variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"

    return f"""{name}:
  enabled: true
{text}"""
