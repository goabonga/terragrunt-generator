# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import contextlib
import os
from typing import Any

import hcl2
from hcl2.utils import SerializationOptions

# python-hcl2 8.x emits a reversible AST by default: block/attribute keys
# and string values keep their surrounding quotes, and every block carries
# an `__is_block__` marker. `strip_string_quotes` unquotes keys and string
# values, and `explicit_blocks=False` drops the marker, yielding the plain
# `{name: {attr: value}}` shape the generator expects.
_HCL2_OPTIONS = SerializationOptions(
    strip_string_quotes=True,
    explicit_blocks=False,
)


def read_file(path: str) -> dict[str, Any]:
    datas: dict[str, Any] = {}
    with open(path) as file:
        datas = hcl2.load(file, serialization_options=_HCL2_OPTIONS)
    return datas


def read_directory(path: str) -> dict[str, Any]:
    datas: dict[str, Any] = {}
    for file in os.listdir(path):
        if file.endswith(".tf"):
            with contextlib.suppress(Exception):
                datas = datas | read_file(f"{path}/{file}")
    return datas
