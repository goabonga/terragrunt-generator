# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

from git.repo.base import Repo


def clone(url: str, path: str, version: str):
    Repo.clone_from(url, path, branch=version)
