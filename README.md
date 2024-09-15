
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
                            [--include | --no-include] -l LOOKUP

Generate terragrunt.hcl configuration from a Terraform module.

Options:
  -h, --help            Show this help message and exit
  -V                    Show program's version number and exit
  -u URL, --url URL     The module repository URL
  -v VERSION, --version VERSION
                        The module version to use
  -p PATH, --path PATH  Define the module path if needed
  --include, --no-include
                        Include or exclude the rendering of the include block (default: True)
  -l LOOKUP, --lookup LOOKUP
                        Define the lookup path
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