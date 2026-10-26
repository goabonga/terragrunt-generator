# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, field

from terragrunt_generator.variables import Variable, VariableKind


def format_description(description: str, indent: str) -> str:
    lines = description.replace('\\"', '"').split("\n")
    formatted = lines[0]
    if len(lines) > 1:
        for line in lines[1:]:
            formatted += f"\n{indent}# {line.lstrip()}"
    return formatted


def get_yaml(name: str, variables: Sequence[Variable], is_enabled: bool = True) -> str:

    name_parts = name.split(".")
    indent = "  " * len(name_parts)

    text = ""
    for kind in (VariableKind.MANDATORY, VariableKind.OPTIONAL, VariableKind.NULLABLE):
        for variable in (v for v in variables if v.kind is kind):
            default = variable.value
            description = format_description(variable.description, indent)

            text += f"{indent}# {variable.name} - {description}\n"
            commented = "# " if kind is not VariableKind.MANDATORY else ""
            text += (
                f"{indent}{commented}{variable.name}: "
                f"{'' if default is None else json.dumps(default)}\n"
            )

    nested_yaml = ""
    current_indent = ""
    for part in name_parts:
        nested_yaml += f"{current_indent}{part}:\n"
        current_indent += "  "

    return f"""{nested_yaml}{current_indent}enabled: {"true" if is_enabled else "false"}
{text}"""


def extract_header(lines: list[str]) -> tuple[list[str], list[str]]:
    header, i = [], 0
    while i < len(lines) and (lines[i].strip().startswith("#") or not lines[i].strip()):
        header.append(lines[i])
        i += 1
    return header, lines[i:]


def is_block_start(line: str, indent: int) -> bool:
    stripped = line.lstrip()
    return (
        len(line) - len(stripped) == indent
        and stripped.endswith(":")
        and not stripped.startswith("#")
    )


COMMENTED_OPTION = re.compile(r"\s*#\s?(\w[\w.-]*):(?:\s|$)")


def option_key(line: str) -> tuple[int, str] | None:
    """The indent and name of a ``key: value`` line, commented out or not."""
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    commented = COMMENTED_OPTION.match(line)
    if commented:
        return indent, commented.group(1)
    if stripped.startswith("#") or ":" not in stripped:
        return None
    return indent, stripped.split(":", 1)[0]


@dataclass
class Block:
    """A key of a level and the lines below it, up to the next key of that level."""

    header: str
    body: list[str] = field(default_factory=list[str])

    @property
    def lines(self) -> list[str]:
        return [self.header, *self.body]


def split_level(lines: list[str], indent: int) -> tuple[list[str], dict[str, Block]]:
    """The lines before the first key of a level, and the blocks of its keys."""
    leading: list[str] = []
    blocks: dict[str, Block] = {}
    current: Block | None = None
    for line in lines:
        if is_block_start(line, indent):
            current = blocks[line.strip()] = Block(line)
        elif current is None:
            leading.append(line)
        else:
            current.body.append(line)
    return leading, blocks


def merge_level(a: list[str], b: list[str], indent: int) -> list[str]:
    """Merge the lines of ``b`` into those of ``a``, which keep their order and values.

    A key of both levels is merged one level down; a key of ``b`` only is added
    after them, and so is any line of ``b`` that ``a`` does not hold yet, unless
    ``a`` already sets that option, commented out or not, to a value of its own.
    """
    leading, blocks_a = split_level(a, indent)
    _, blocks_b = split_level(b, indent)

    merged = list(leading)
    for key, block in blocks_a.items():
        merged.append(block.header)
        other = blocks_b.get(key)
        if other is None:
            merged.extend(block.body)
        else:
            merged.extend(merge_level(block.body, other.body, indent + 2))

    for key, block in blocks_b.items():
        if key not in blocks_a:
            merged.extend(block.lines)

    options = {option for option in map(option_key, merged) if option}
    for line in b:
        if is_block_start(line, indent) or line in merged:
            continue
        option = option_key(line)
        if option in options:
            continue
        merged.append(line)
        if option:
            options.add(option)

    return merged


def merge_yaml_strings(yaml1: str, yaml2: str) -> str:
    lines1, lines2 = yaml1.strip().splitlines(), yaml2.strip().splitlines()
    header1, body1 = extract_header(lines1)
    _, body2 = extract_header(lines2)

    merged_body = merge_level(body1, body2, indent=0)
    return "\n".join(header1 + [""] + merged_body)
