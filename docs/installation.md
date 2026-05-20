# Installation

## Requirements

- Python 3.13+

## From PyPI

```bash
pip install terragrunt-generator
```

Or run it without installing, using [uv](https://docs.astral.sh/uv/):

```bash
uvx terragrunt-generator --help
```

## From source

```bash
git clone https://github.com/goabonga/terragrunt-generator.git
cd terragrunt-generator
uv sync
uv run terragrunt-generator --help
```

See [CONTRIBUTING.md](https://github.com/goabonga/terragrunt-generator/blob/main/CONTRIBUTING.md)
for the development workflow (ruff, mypy, pytest, pre-commit).
