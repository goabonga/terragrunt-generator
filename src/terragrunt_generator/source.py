# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from shutil import copytree

from terragrunt_generator.git import clone
from terragrunt_generator.utils import is_local


@dataclass(frozen=True)
class ModuleSource(ABC):
    """Where a Terraform module comes from, and how the generated files point at it."""

    url: str
    version: str
    path: str | None = None

    @abstractmethod
    def fetch(self, dest: str) -> None:
        """Bring the module into ``dest``."""

    @property
    def is_http(self) -> bool:
        return "http" in self.url

    @property
    def name(self) -> str:
        """The module name: its sub-path, or the last directory of its URL."""
        if self.path is not None:
            return self.path.split("/")[-1]
        return os.path.dirname(self.url).split("/")[-1].replace(".git", "")

    @property
    def web_url(self) -> str:
        """The page of the module, as linked in the header of the generated file."""
        if not self.is_http:
            return self.url
        return f"{self.url.replace('.git', '')}/tree/{self.version}/{self.path or ''}"

    @property
    def terragrunt_source(self) -> str:
        """The expression that the generated ``locals.source`` is set to."""
        if not self.is_http:
            return f'find_in_parent_folders("{self.url}")'
        bare = self.url.replace("https://", "").replace("http://", "")
        sub_path = f"//{self.path}" if self.path is not None else ""
        return f'"{bare}{sub_path}?ref={self.version}"'


class LocalSource(ModuleSource):
    def fetch(self, dest: str) -> None:
        copytree(self.url, dest)


class GitSource(ModuleSource):
    def fetch(self, dest: str) -> None:
        clone(self.url, dest, self.version)


def module_source(url: str, version: str, path: str | None = None) -> ModuleSource:
    """A local directory is copied, anything else is cloned."""
    source = LocalSource if is_local(url) else GitSource
    return source(url, version, path)
