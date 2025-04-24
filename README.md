
# 🚀 terragrunt-generator 🎉

[![codecov](https://codecov.io/gh/goabonga/terragrunt-generator/branch/main/graph/badge.svg?token=LZYOP61FF7)](https://codecov.io/gh/goabonga/terragrunt-generator)

## 🪄 What is terragrunt-generator?

**terragrunt-generator** is your one-stop tool to automatically generate `terragrunt.hcl` files with well-documented inputs from variables exposed by Terraform modules. The magic happens with a simple **YAML** configuration file, making your setup process as smooth as butter! 🧈✨

## 📋 Requirements

- Python 3.6+

## 🔧 Installation

```bash
pip install terragrunt-generator
```

## 🎯 Usage

### 🔍 Command Overview

```bash
terragrunt-generator --help
```

You'll see something like this:

```plaintext
usage: terragrunt-generator [-h] [-V] -u URL [-v VERSION] [-p PATH]
                            [--include | --no-include] -l LOOKUP [-o OUTPUT]
                            [--yaml-output YAML_OUTPUT]
                            [--yaml-for-env YAML_FOR_ENV]
                            [--enabled | --no-enabled]

Generate a terragrunt.hcl configuration file from a Terraform module.

options:
  -h, --help            show this help message and exit
  -V                    show program's version number and exit
  -u URL, --url URL     URL or local path to the Terraform module (can be a
                        git repo or directory).
  -v VERSION, --version VERSION
                        Branch, tag, or commit hash to checkout if the module
                        is from a git repository (default: main).
  -p PATH, --path PATH  Relative path to the module inside the repository or
                        directory (if needed).
  --include, --no-include
                        Whether to include the "include" block in the
                        generated terragrunt.hcl (default: true).
  -l LOOKUP, --lookup LOOKUP
                        Path used for variable lookup in the generated
                        Terragrunt configuration.
  -o OUTPUT, --output OUTPUT
                        File path to write the generated terragrunt.hcl
                        (default: print to stdout).
  --yaml-output YAML_OUTPUT
                        Directory to write the generated YAML config file (it
                        will be merged if it already exists).
  --yaml-for-env YAML_FOR_ENV
                        Environment name used to generate the YAML file (e.g.,
                        config.dev.yaml).
  --enabled, --no-enabled
                        Whether to mark the module as enabled in the YAML
                        configuration (default: true).

```

### 📚 Example Usage

```bash
terragrunt-generator \
-u https://github.com/terraform-google-modules/terraform-google-project-factory.git \
-v v14.2.1 \
-l 'project'
```

### 📝 Sample Output

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

## 🙌 Contribute

Got a cool idea? Found a bug? Contributions are welcome! Check out our [contributing guidelines](CONTRIBUTING.md) and help make `terragrunt-generator` even better! 🚀

---

Enjoy automating your Terragrunt configurations with ease! 🎉