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


def group_by_indent(lines):
    blocks = {}
    current_key = None
    current_block = []
    for line in lines:
        if not line.strip():
            if current_key:
                current_block.append(line)
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if indent == 2 and stripped.endswith(":"):
            if current_key is not None:
                blocks[current_key] = current_block
            current_key = stripped[:-1]
            current_block = [line]
        else:
            if current_key:
                current_block.append(line)
    if current_key:
        blocks[current_key] = current_block
    return blocks


def merge_blocks(block1, block2):
    merged = dict(block1)
    for key, block in block2.items():
        if key not in merged:
            merged[key] = block
    return merged


def extract_yaml_parts(lines):
    header = []
    i = 0
    while i < len(lines) and (
        not lines[i].strip().endswith(':') or lines[i].startswith('#')
    ):
        header.append(lines[i])
        i += 1
    top_key = lines[i].strip()
    body = lines[i + 1 :]
    return header, top_key, body


def merge_yaml_strings(yaml1: str, yaml2: str) -> str:
    lines1 = yaml1.strip().splitlines()
    lines2 = yaml2.strip().splitlines()

    header1, top_key, body1 = extract_yaml_parts(lines1)
    _, _, body2 = extract_yaml_parts(lines2[lines2.index(top_key) :])

    blocks1 = group_by_indent(body1)
    blocks2 = group_by_indent(body2)
    merged_blocks = merge_blocks(blocks1, blocks2)

    result = [top_key]
    for key, block in merged_blocks.items():
        result.extend(block)

    return "\n".join(header1 + result)
