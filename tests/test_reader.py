from unittest.mock import MagicMock, mock_open, patch

from generator.reader import read_directory, read_file

data: str = """
variable "test" {
    default = ""
    type = "string"
}
"""


@patch('builtins.open', new_callable=mock_open, read_data=data)
def test_read_file(mock_file):
    path = 'path/to/open'
    results = read_file(path=path)
    mock_file.assert_called_with(path)
    assert results == {'variable': [{'test': {'default': '', 'type': 'string'}}]}


@patch('builtins.open', new_callable=mock_open, read_data=data)
@patch('hcl2.load', MagicMock(side_effect=Exception('mocked error')))
def test_read_file_except(mock_file):
    path = 'path/to/open'
    error = None
    try:
        read_file(path=path)
    except Exception as e:
        error = e
    assert error is not None


@patch('os.listdir', return_value=['test.tf'])
@patch('builtins.open', new_callable=mock_open, read_data=data)
def test_read_directory(mock_file, mock_directory):
    path = 'path/to/open'
    results = read_directory(path)
    mock_directory.assert_called_with(path)
    mock_file.assert_called_with(f'{path}/test.tf')
    assert results == {'variable': [{'test': {'default': '', 'type': 'string'}}]}
