# terragrunt-generator

**terragrunt-generator** generates `terragrunt.hcl` configuration files —
with documented inputs — from the variables exposed by a Terraform module.
Point it at a module (a git repository or a local directory), tell it where
to look up values, and it emits a ready-to-edit Terragrunt manifest plus an
optional YAML config skeleton.

## What it does

- Reads the `variable` blocks of a Terraform module.
- Splits them into mandatory, optional and nullable inputs.
- Renders a `terragrunt.hcl` with `include`, `locals`, `terraform` and
  `inputs` blocks wired to a `yamldecode`-based config lookup.
- Optionally writes (and merges) per-environment `config.<env>.yaml` files.

## At a glance

```bash
terragrunt-generator \
  -u https://github.com/terraform-google-modules/terraform-google-project-factory.git \
  -v v14.2.1 \
  -l 'project'
```

See [Installation](installation.md) to get the CLI, [Usage](usage.md) for the
full option reference and worked examples, and
[Stability & deprecation](stability.md) for the versioning contract.

The source lives on
[GitHub](https://github.com/goabonga/terragrunt-generator); releases are
automated from [Conventional Commits](https://www.conventionalcommits.org/)
by [multicz](https://github.com/goabonga/multicz).
