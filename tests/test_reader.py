# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

from unittest.mock import MagicMock, mock_open, patch

from terragrunt_generator.reader import read_directory, read_file

data: str = """
variable "test" {
    default = ""
    type = "string"
}
"""


@patch("builtins.open", new_callable=mock_open, read_data=data)
def test_read_file(mock_file):
    path = "path/to/open"
    results = read_file(path=path)
    mock_file.assert_called_with(path)
    assert results == {"variable": [{"test": {"default": "", "type": "string"}}]}


@patch("builtins.open", new_callable=mock_open, read_data=data)
@patch("hcl2.loads", MagicMock(side_effect=Exception("mocked error")))
def test_read_file_except(mock_file):
    path = "path/to/open"
    error = None
    try:
        read_file(path=path)
    except Exception as e:
        error = e
    assert error is not None


heredoc_data: str = (
    'variable "test" {\n'
    "  description = <<DESC\n"
    "  some text\n"
    "DESC \n"  # trailing whitespace after the terminator
    '  type = "string"\n'
    "}\n"
)


@patch("builtins.open", new_callable=mock_open, read_data=heredoc_data)
def test_read_file_heredoc_trailing_whitespace(mock_file):
    # Regression: a heredoc terminator with trailing whitespace (`DESC `) is
    # rejected by python-hcl2; read_file strips trailing whitespace per line so
    # such (Terraform-valid) files still parse.
    results = read_file(path="path/to/open")
    assert "variable" in results
    assert results["variable"][0]["test"]["type"] == "string"


@patch("os.listdir", return_value=["README.md", "test.tf"])
@patch("builtins.open", new_callable=mock_open, read_data=data)
def test_read_directory(mock_file, mock_directory):
    path = "path/to/open"
    results = read_directory(path)
    mock_directory.assert_called_with(path)
    # Only the .tf file is opened; non-.tf entries (README.md) are skipped.
    mock_file.assert_called_once_with(f"{path}/test.tf")
    assert results == {"variable": [{"test": {"default": "", "type": "string"}}]}


@patch("os.listdir", return_value=["test.tf", "test.tf"])
@patch("builtins.open", new_callable=mock_open, read_data=data)
@patch("hcl2.loads", MagicMock(side_effect=Exception("mocked error")))
def test_read_directory_except(mock_file, mock_directory):
    path = "path/to/open"
    results = read_directory(path)
    mock_directory.assert_called_with(path)
    mock_file.assert_called_with(f"{path}/test.tf")
    assert results == {}
