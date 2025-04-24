import json


def get_yaml(name: str, variables) -> str:
    name_parts = name.split('.')

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

            text += f"{indent}# {variable['name']} - {description}\n"
            if var_type == 'nullables':
                text += f"{indent}# {variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"
            elif var_type == 'optionals':
                text += f"{indent}# {variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"
            else:
                text += f"{indent}{variable['name']}: {json.JSONEncoder().encode(default) if default else ''}\n"

    nested_yaml = ''
    current_indent = ''
    for part in name_parts:
        nested_yaml += f"{current_indent}{part}:\n"
        current_indent += '  '

    return f"""{nested_yaml}{current_indent}enabled: true
{text}"""


def extract_header(lines):
    header = []
    i = 0
    while i < len(lines) and (lines[i].strip().startswith("#") or not lines[i].strip()):
        header.append(lines[i])
        i += 1
    return header, lines[i:]


def extract_top_level_blocks(lines):
    blocks = {}
    current_key = None
    current_block = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_block is not None:
                current_block.append(line)
            continue

        indent = len(line) - len(stripped)
        if indent == 0 and stripped.endswith(":") and not stripped.startswith("#"):
            if current_key and current_block:
                blocks[current_key] = current_block
            current_key = stripped
            current_block = [line]
        else:
            if current_block is not None:
                current_block.append(line)

    if current_key and current_block:
        blocks[current_key] = current_block

    return blocks


def merge_top_blocks(blocks1, blocks2):
    merged = dict(blocks1)
    for key, block in blocks2.items():
        if key in merged:
            merged_block = merged[key]
            merged_block.extend([line for line in block if line not in merged_block])
            merged[key] = merged_block
        else:
            merged[key] = block
    return merged


def merge_yaml_strings(yaml1: str, yaml2: str) -> str:
    lines1 = yaml1.strip().splitlines()
    lines2 = yaml2.strip().splitlines()

    header1, body1 = extract_header(lines1)
    _, body2 = extract_header(lines2)

    blocks1 = extract_top_level_blocks(body1)
    blocks2 = extract_top_level_blocks(body2)

    merged_blocks = merge_top_blocks(blocks1, blocks2)

    result = header1 + ['']
    for block in merged_blocks.values():
        result.extend(block)

    return "\n".join(result)
