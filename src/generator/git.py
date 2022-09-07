from git.repo.base import Repo


def clone(url: str, path: str, version: str):
    Repo.clone_from(url, path, branch=version)
