from unittest.mock import patch

from generator.git import clone


@patch('generator.git.Repo.clone_from')
def test_clone_repo(repo):
    url: str = 'https://gitserver.com/test/test.git'
    path: str = 'moudles/test'
    version: str = '0.1.0'
    clone(url, path, version)
    repo.assert_called_with(url, path, branch=version)
