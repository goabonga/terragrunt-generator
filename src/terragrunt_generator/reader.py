# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import contextlib
import os
from typing import Any

import hcl2


def read_file(path: str) -> dict[str, Any]:
    datas: dict[str, Any] = {}
    with open(path) as file:
        datas = hcl2.load(file)  # type: ignore[attr-defined]
    return datas


def read_directory(path: str) -> dict[str, Any]:
    datas: dict[str, Any] = {}
    for file in os.listdir(path):
        if file.endswith(".tf"):
            with contextlib.suppress(Exception):
                datas = datas | read_file(f"{path}/{file}")
    return datas
