# terragrunt-generator

**terragrunt-generator** provide a way to generate a ```terragrunt.hcl``` file with documented inputs who's coming from variables exposed by terraform module.

The result is easily configurable with a **yaml** file.
## Requirements

- python3.6+

## Instalation

```
$ pip install terragrunt-generator
```

## Usages

### Exec

```
terragrunt-generator -u https://github.com/goabonga/terragrunt-generator.git -v main -p /examples/modules

```

### Results

```
# modules main
#
# yaml config
# ```
# modules:
#   enabled: true
#   required:
#   optional: "optional"
#   # nullable:
# ```
#
include {
    path = "${find_in_parent_folders()}"
}

locals {
    all = merge(
        yamldecode(file("find_in_parent_folders("config.yaml")")),
    )
}

terraform {
    source = lookup(local.all["modules"], "enabled", true) == true ? "https://github.com/goabonga/terragrunt-generator.git////examples/modules?ref=main" : null
}

inputs = merge({
    # required - required value - required
    required = lookup(local.all["modules"], "required", "None")
    # optional - optional value
    optional = lookup(local.all["modules"], "optional", "optional")

},
  # nullable - nullable value
  (lookup(local.all["modules"], "nullable", null) == null ? {} : { nullable =  lookup(local.all["modules"], "nullable") })
)

```
