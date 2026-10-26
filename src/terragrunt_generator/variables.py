# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

from dataclasses import dataclass
from enum import Enum
from typing import Any


class VariableKind(Enum):
    """How a Terraform variable is expected to be set."""

    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    NULLABLE = "nullable"


class _NoDefault:
    """Marks a variable declared without a ``default``."""

    def __repr__(self) -> str:
        return "NO_DEFAULT"


NO_DEFAULT = _NoDefault()


@dataclass(frozen=True)
class Variable:
    """A Terraform ``variable`` block, as the generator needs it."""

    name: str
    description: str = ""
    type: str | None = None
    default: Any = NO_DEFAULT

    @property
    def kind(self) -> VariableKind:
        if self.default is NO_DEFAULT:
            return VariableKind.MANDATORY
        if self.default is None:
            return VariableKind.NULLABLE
        return VariableKind.OPTIONAL

    @property
    def value(self) -> Any:
        """The declared default, or ``None`` when there is none."""
        return None if self.default is NO_DEFAULT else self.default

    @classmethod
    def from_block(cls, name: str, block: dict[str, Any]) -> "Variable":
        raw_type = block.get("type")
        return cls(
            name=name,
            description=block.get("description", ""),
            # Terraform wraps type expressions in `${...}` once parsed.
            type=None
            if raw_type is None
            else raw_type.replace("${", "").replace("}", ""),
            default=block.get("default", NO_DEFAULT),
        )


def parse_variables(blocks: list[dict[str, Any]]) -> list[Variable]:
    """The variables of the ``variable`` blocks of a module, in declaration order."""
    return [
        Variable.from_block(name, block)
        for entry in blocks
        for name, block in entry.items()
    ]
