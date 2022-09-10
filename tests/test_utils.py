from generator.utils import is_local


def test_is_local():
    assert is_local('/tmp') is True
    assert is_local('https://example.com') is False
