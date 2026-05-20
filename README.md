# terragrunt-generator

[![CI](https://github.com/goabonga/terragrunt-generator/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/goabonga/terragrunt-generator/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/github/goabonga/terragrunt-generator?logo=codecov)](https://codecov.io/gh/goabonga/terragrunt-generator)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/goabonga/terragrunt-generator/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

**terragrunt-generator** generates `terragrunt.hcl` configuration files — with
documented inputs — from the variables exposed by a Terraform module. Point it
at a module (a git repository or a local directory), tell it where to look up
values, and it emits a ready-to-edit Terragrunt manifest plus an optional YAML
config skeleton.

## Documentation

The project site is published from `main` to GitHub Pages:
<https://goabonga.github.io/terragrunt-generator/>.

## Requirements

- Python 3.13+

## Installation

```bash
pip install terragrunt-generator
```

Or run it without installing, using [uv](https://docs.astral.sh/uv/):

```bash
uvx terragrunt-generator --help
```

## Usage

```bash
terragrunt-generator \
  -u https://github.com/terraform-google-modules/terraform-google-project-factory.git \
  -v v14.2.1 \
  -l 'project'
```

This reads the module's `variable` blocks and prints a `terragrunt.hcl` whose
`inputs` are wired to a `yamldecode`-based config lookup:

```hcl
# terraform-google-modules v14.2.1
# https://github.com/terraform-google-modules/terraform-google-project-factory/tree/v14.2.1/

include {
    path = find_in_parent_folders()
}

locals {
    source = "github.com/terraform-google-modules/terraform-google-project-factory.git?ref=v14.2.1"
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}

terraform {
    source = lookup(local.all, "project", false) == false ? null : lookup(local.all.project, "enabled", false) == false ? null : local.source
}

inputs = merge({
    billing_account = lookup(local.all.project, "billing_account", "")
    name = lookup(local.all.project, "name", "")
    org_id = lookup(local.all.project, "org_id", "")
    activate_api_identities = lookup(local.all.project, "activate_api_identities", [])
    activate_apis = lookup(local.all.project, "activate_apis", ["compute.googleapis.com"])
})
```

See the [usage guide](https://goabonga.github.io/terragrunt-generator/usage/)
for the full option reference and the per-environment YAML workflow.

## Development

```bash
git clone https://github.com/goabonga/terragrunt-generator.git
cd terragrunt-generator
uv sync

# Quality gates (mirrored in CI).
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
uv run pytest --cov=terragrunt_generator

# Install the pre-commit + commit-msg hooks.
uv run pre-commit install
```

## Versioning and release

Releases are automated. Every push to `main` runs
`multicz bump --commit --tag --push` — driven by
[Conventional Commits](https://www.conventionalcommits.org/) — then publishes
to PyPI and deploys the docs.

```bash
# Preview the next release against the current branch.
multicz status
```

## Contributing

See [CONTRIBUTING.md](https://github.com/goabonga/terragrunt-generator/blob/main/CONTRIBUTING.md)
for the workflow, the commit-message convention, and the test/lint
expectations. By participating you agree to the
[Code of Conduct](https://github.com/goabonga/terragrunt-generator/blob/main/CODE_OF_CONDUCT.md).

Security issues: please follow the disclosure process in
[SECURITY.md](https://github.com/goabonga/terragrunt-generator/blob/main/SECURITY.md).

## License

Distributed under the
[MIT License](https://github.com/goabonga/terragrunt-generator/blob/main/LICENSE).
