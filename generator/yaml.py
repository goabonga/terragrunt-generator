import json


def get_yaml(name: str, variables) -> str:
    # Split the name to handle nested structures dynamically
    name_parts = name.split('.')

    # Initialize the YAML structure with correct indentation for nested levels
    indent = '  ' * len(name_parts)

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
            # Indent variables according to the nesting level
            text += f"{indent}# {variable['name']} - {description}\n"
            if var_type == 'nullables':
                text += f"{indent}# {variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"
            elif var_type == 'optionals':
                text += f"{indent}# {variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"
            else:
                text += f"{indent}{variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"

    # Create the nested YAML structure dynamically
    nested_yaml = ''
    current_indent = ''
    for part in name_parts:
        nested_yaml += f"{current_indent}{part}:\n"
        current_indent += '  '  # Increase indentation for each level

    # Combine the nested structure with the variables
    return f"""{nested_yaml}{current_indent}enabled: true
{text}"""
