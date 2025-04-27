import json


def format_description(description: str, indent: str) -> str:
    lines = description.replace('\\"', '"').split('\n')
    # if not lines:
    #     return ''
    formatted = lines[0]
    if len(lines) > 1:
        for line in lines[1:]:
            formatted += f'\n{indent}# {line.lstrip()}'
    return formatted


def get_yaml(name: str, variables, is_enabled: bool = True) -> str:

    name_parts = name.split('.')
    indent = '  ' * len(name_parts)

    text = ''
    for var_type in ('mandatories', 'optionals', 'nullables'):
        for variable in variables.get(var_type, []):
            default = variable.get('default')
            description = format_description(variable.get('description', ''), indent)

            text += f"{indent}# {variable['name']} - {description}\n"
            if var_type == 'nullables':
                text += f"{indent}# {variable['name']}: {json.dumps(default) if default else ''}\n"
            elif var_type == 'optionals':
                text += f"{indent}# {variable['name']}: {json.dumps(default) if default else ''}\n"
            else:
                text += f"{indent}{variable['name']}: {json.dumps(default) if default else ''}\n"

    nested_yaml = ''
    current_indent = ''
    for part in name_parts:
        nested_yaml += f"{current_indent}{part}:\n"
        current_indent += '  '

    return f"""{nested_yaml}{current_indent}enabled: {"true" if is_enabled else "false"}
{text}"""


def extract_header(lines: list[str]) -> tuple[list[str], list[str]]:
    header, i = [], 0
    while i < len(lines) and (lines[i].strip().startswith('#') or not lines[i].strip()):
        header.append(lines[i])
        i += 1
    return header, lines[i:]


def is_block_start(line: str, indent: int) -> bool:
    stripped = line.lstrip()
    return (
        len(line) - len(stripped) == indent
        and stripped.endswith(':')
        and not stripped.startswith('#')
    )


def split_blocks(
    lines: list[str], indent: int
) -> tuple[dict[str, list[str]], list[str]]:
    blocks, order, i = {}, [], 0
    while i < len(lines):
        if is_block_start(lines[i], indent):
            key = lines[i].strip()
            start = i
            i += 1
            while i < len(lines) and not is_block_start(lines[i], indent):
                i += 1
            blocks[key] = lines[start:i]
            order.append(key)
        else:
            i += 1
    return blocks, order


def merge_block_lines(a: list[str], b: list[str], indent: int) -> list[str]:
    blocks_a, order_a = split_blocks(a, indent)
    blocks_b, order_b = split_blocks(b, indent)

    merged, done = [], set()
    i = 0
    while i < len(a):
        line = a[i]
        if is_block_start(line, indent):
            key = line.strip()
            block_a = blocks_a[key]
            if key in blocks_b:
                block_b = blocks_b[key]
                merged_sub = merge_block_lines(block_a[1:], block_b[1:], indent + 2)
                merged.extend([block_a[0], *merged_sub])
                done.add(key)
            else:
                merged.extend(block_a)
            i += len(block_a)
        else:
            merged.append(line)
            i += 1

    for key in order_b:
        if key not in done and key not in blocks_a:
            merged.extend(blocks_b[key])

    for line in b:
        if is_block_start(line, indent):
            continue
        if line not in merged:
            merged.append(line)

    return merged


def merge_yaml_strings(yaml1: str, yaml2: str) -> str:
    lines1, lines2 = yaml1.strip().splitlines(), yaml2.strip().splitlines()
    header1, body1 = extract_header(lines1)
    _, body2 = extract_header(lines2)

    merged_body = merge_block_lines(body1, body2, indent=0)
    return "\n".join(header1 + [""] + merged_body)
