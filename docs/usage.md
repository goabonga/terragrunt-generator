# Usage

## Command overview

```bash
terragrunt-generator --help
```

```plaintext
usage: terragrunt-generator [-h] [-V] -u URL [-v VERSION] [-p PATH]
                            [--include | --no-include] -l LOOKUP [-o OUTPUT]
                            [--yaml-output YAML_OUTPUT]
                            [--yaml-for-env YAML_FOR_ENV]
                            [--enabled | --no-enabled]
```

## Options

| Option | Description |
| --- | --- |
| `-u`, `--url` | URL or local path to the Terraform module (git repo or directory). **Required.** |
| `-v`, `--version` | Branch, tag or commit to checkout for a git module (default: `main`). |
| `-p`, `--path` | Relative path to the module inside the repository or directory. |
| `--include` / `--no-include` | Whether to emit the `include` block (default: include). |
| `-l`, `--lookup` | Path used for variable lookup in the generated config. **Required.** |
| `-o`, `--output` | File (or directory) to write `terragrunt.hcl` to (default: stdout). |
| `--yaml-output` | Directory to write the generated YAML config (repeatable; merged if it exists). |
| `--yaml-for-env` | Environment name(s) for the YAML file, e.g. `config.dev.yaml` (repeatable). |
| `--enabled` / `--no-enabled` | Mark the module as enabled in the YAML config (default: enabled). |

## Example

```bash
terragrunt-generator \
  -u https://github.com/terraform-google-modules/terraform-google-project-factory.git \
  -v v14.2.1 \
  -l 'project'
```

### Sample output

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

## Per-environment YAML

Generate (and merge into) environment-specific config files:

```bash
terragrunt-generator \
  -u ./modules/network \
  -l 'network' \
  --yaml-output ./live/ \
  --yaml-for-env dev \
  --yaml-for-env prod
```

This writes `live/config.dev.yaml` and `live/config.prod.yaml`, merging with
any existing content rather than overwriting it.

## End-to-end example

For a complete, realistic flow — scaffolding a repository with Cookiecutter and
populating a whole GCP foundation (network, KMS, GKE, …) with
`terragrunt-generator` — see
[Bootstrap a GCP infra](bootstrap-gcp.md).
