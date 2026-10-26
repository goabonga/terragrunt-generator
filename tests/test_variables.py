# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import pytest

from terragrunt_generator.variables import (
    NO_DEFAULT,
    Variable,
    VariableKind,
    parse_variables,
)


@pytest.mark.parametrize(
    ("default", "kind"),
    [
        (NO_DEFAULT, VariableKind.MANDATORY),
        (None, VariableKind.NULLABLE),
        ("hello", VariableKind.OPTIONAL),
        ("", VariableKind.OPTIONAL),
        (False, VariableKind.OPTIONAL),
        (0, VariableKind.OPTIONAL),
        ([], VariableKind.OPTIONAL),
    ],
)
def test_the_kind_follows_the_default(default, kind):
    assert Variable("v", default=default).kind is kind


def test_a_variable_without_default_is_mandatory_by_default():
    assert Variable("v").kind is VariableKind.MANDATORY


def test_the_value_is_none_without_a_default():
    assert Variable("v").value is None
    assert Variable("v", default=None).value is None
    assert Variable("v", default=3).value == 3


def test_variables_are_immutable():
    with pytest.raises(AttributeError):
        Variable("v").name = "w"


def test_parse_variables():
    blocks = [
        {
            "test": {"description": "A", "type": "string", "default": None},
            "test1": {"description": "A", "type": "string", "default": "hello"},
            "test2": {"description": "A", "type": "string"},
        }
    ]

    assert parse_variables(blocks) == [
        Variable("test", "A", "string", None),
        Variable("test1", "A", "string", "hello"),
        Variable("test2", "A", "string"),
    ]
    assert [v.kind for v in parse_variables(blocks)] == [
        VariableKind.NULLABLE,
        VariableKind.OPTIONAL,
        VariableKind.MANDATORY,
    ]


def test_parse_variables_keeps_the_declaration_order_across_blocks():
    blocks = [{"b": {}}, {"a": {}, "c": {}}]

    assert [v.name for v in parse_variables(blocks)] == ["b", "a", "c"]


def test_parse_variables_unwraps_the_type_expression():
    (variable,) = parse_variables([{"v": {"type": "${list(string)}"}}])

    assert variable.type == "list(string)"


def test_parse_variables_without_type_nor_description():
    (variable,) = parse_variables([{"v": {}}])

    assert variable == Variable("v")
    assert variable.type is None
    assert variable.description == ""


def test_parse_variables_without_variable_blocks():
    assert parse_variables([]) == []


def test_a_missing_default_is_readable_in_the_representation():
    assert repr(Variable("v")) == (
        "Variable(name='v', description='', type=None, default=NO_DEFAULT)"
    )
