# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

from terragrunt_generator.utils import is_local


def test_is_local():
    assert is_local('/tmp') is True
    assert is_local('https://example.com') is False
