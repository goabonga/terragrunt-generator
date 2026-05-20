# Example: bootstrap a full GCP infrastructure

This walkthrough shows terragrunt-generator in a realistic end-to-end flow:
scaffold a repository with a [Cookiecutter](https://cookiecutter.readthedocs.io/)
template, then **populate** it module by module with `terragrunt-generator`.

Two tools, two distinct jobs:

| Tool | Responsibility |
| --- | --- |
| [`cookiecutter-terragrunt-project`](https://github.com/goabonga/cookiecutter-terragrunt-project) | Scaffolds the repo skeleton: the **root** `terragrunt.hcl` (providers, GCS remote state, Terraform version), the `config.<env>.yaml` seed, and shell helpers. |
| [`terragrunt-generator`](https://github.com/goabonga/terragrunt-generator) | Generates one **child** `terragrunt.hcl` per Terraform module and merges that module's documented inputs into `config.<env>.yaml`. |

The result is a DRY, multi-environment Terragrunt repository where every
module's source and inputs are declared once, and all values live in a single
per-environment YAML file.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — runs both `cookiecutter` and
  `terragrunt-generator` on demand via `uvx` (no manual install; uv also
  provisions a suitable Python)
- [Terraform](https://www.terraform.io) and [Terragrunt](https://terragrunt.gruntwork.io)
- [`gcloud`](https://cloud.google.com/sdk/docs/install) authenticated against your project

## Step 1 — scaffold the repository

The template is non-interactive friendly. Feed it a default context and let it
generate the project (the slug `gcp_infrastructure` is derived from
`project_name`):

```bash
tmpfile=$(mktemp)
cat <<'EOF' > "$tmpfile"
default_context:
  full_name: "Chris"
  email: "goabonga@pm.me"
  github_username: "goabonga"
  project_name: "GCP Infrastructure"
  remote_state_bucket_name: ""
  default_environment: "dev"
EOF

uvx cookiecutter -f --no-input --config-file "$tmpfile" \
  https://github.com/goabonga/cookiecutter-terragrunt-project.git
rm "$tmpfile"
```

### What the scaffold gives you

```
gcp_infrastructure/
├── .bashrc                 # terragrunt helper functions (switch_env, plan, apply, …)
├── config.dev.yaml         # per-environment values (starts with remote_state.bucket)
└── google/
    └── terragrunt.hcl      # the ROOT config every module inherits
```

The root `google/terragrunt.hcl` is the parent that each generated module
includes via `find_in_parent_folders()`. It wires up three things:

- **Environment + values** — `local.environment` from `get_env("ENV", "dev")`,
  and `local.config` merged from `config.<env>.yaml`.
- **Remote state** — a `gcs` backend keyed by
  `<environment>/<path_relative_to_include>`, so every module gets an isolated
  state path automatically.
- **Generated provider + versions files** — `google` / `google-beta` providers
  and a `required_version` pin, regenerated on each run.

```hcl
locals {
  environment = get_env("ENV", "dev")
  config = merge(
    yamldecode(file(find_in_parent_folders(format("config.%s.yaml", local.environment)))),
  )
}

remote_state {
  backend = "gcs"
  config = {
    bucket = "${local.config.remote_state.bucket}"
    prefix = "${format("%s/%s", local.environment, path_relative_to_include())}"
  }
  generate = { path = "generated_backend.tf", if_exists = "overwrite_terragrunt" }
}
```

Set your state bucket in `config.dev.yaml`:

```yaml
remote_state:
  bucket: my-tf-state-bucket
```

## Step 2 — populate modules with terragrunt-generator

Move into the generated project, then generate one module per Terraform
source. With [uv](https://docs.astral.sh/uv/), `uvx terragrunt-generator`
fetches and runs the tool in a cached, ephemeral environment — no virtualenv
to create or activate:

```bash
cd gcp_infrastructure
```

Each invocation follows the same pattern:

```bash
uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-network.git \
    -v v10.0.0 \
    -p modules/vpc \
    -l network.vpc \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/vpc
```

What that one command does:

- `-u` / `-v` / `-p` — the module's git source, ref, and subpath. The child
  `terragrunt.hcl` pins `terraform.source` to exactly this.
- `-l network.vpc` — the **lookup key**. Inputs resolve from
  `local.all.network.vpc.*`, and the module is gated on
  `network.vpc.enabled` in the YAML.
- `--output google/network/vpc` — where the child `terragrunt.hcl` is written.
  Its `include { path = find_in_parent_folders() }` finds the root
  `google/terragrunt.hcl`.
- `--yaml-output ./` + `--yaml-for-env dev` — append (and **merge**, never
  overwrite) the module's documented inputs under the `network.vpc` key of
  `config.dev.yaml`.

Run it once per module. The reference bootstrap builds a full GCP foundation
from Google's official modules:

| Area | Lookup key(s) | Output path under `google/` |
| --- | --- | --- |
| [Cloud DNS](https://github.com/terraform-google-modules/terraform-google-cloud-dns) | `network.dns.internal`, `network.dns.external` | `network/dns/{internal,external}` |
| [VPC / subnets](https://github.com/terraform-google-modules/terraform-google-network) | `network.vpc`, `network.subnets` | `network/{vpc,subnets}` |
| [Firewall / routes / peering](https://github.com/terraform-google-modules/terraform-google-network) | `network.firewall`, `network.routes`, `network.peering` | `network/{firewall,routes,peering}` |
| [NAT](https://github.com/terraform-google-modules/terraform-google-cloud-nat) | `network.nat` | `network/nat` |
| [Addresses](https://github.com/terraform-google-modules/terraform-google-address) | `network.address.internal`, `network.address.external` | `network/address/{internal,external}` |
| [KMS](https://github.com/terraform-google-modules/terraform-google-kms) | `kms` | `kms` |
| [Artifact Registry](https://github.com/GoogleCloudPlatform/terraform-google-artifact-registry) | `registries.docker` | `registries/docker` |
| [Cloud Storage](https://github.com/terraform-google-modules/terraform-google-cloud-storage) | `buckets` | `buckets` |
| [Log export / bucket](https://github.com/terraform-google-modules/terraform-google-log-export) | `log.logexport`, `log.logbucket` | `log/{logexport,logbucket}` |
| [GKE cluster / workload identity](https://github.com/terraform-google-modules/terraform-google-kubernetes-engine) | `gke.cluster`, `gke.workload-identity` | `gke/{cluster,workload-identity}` |

### Resulting structure

```
gcp_infrastructure/
├── .bashrc
├── config.dev.yaml                 # every module's inputs, merged under one tree
└── google/
    ├── terragrunt.hcl              # root: providers, GCS backend, versions
    ├── network/
    │   ├── dns/{internal,external}/terragrunt.hcl
    │   ├── vpc/terragrunt.hcl
    │   ├── subnets/terragrunt.hcl
    │   ├── firewall/terragrunt.hcl
    │   ├── routes/terragrunt.hcl
    │   ├── peering/terragrunt.hcl
    │   ├── nat/terragrunt.hcl
    │   └── address/{internal,external}/terragrunt.hcl
    ├── kms/terragrunt.hcl
    ├── registries/docker/terragrunt.hcl
    ├── buckets/terragrunt.hcl
    ├── log/{logexport,logbucket}/terragrunt.hcl
    └── gke/{cluster,workload-identity}/terragrunt.hcl
```

`config.dev.yaml` mirrors that tree — one block per lookup key, each commented
with the module's variable documentation so you know what to fill in:

```yaml
remote_state:
  bucket: my-tf-state-bucket
network:
  vpc:
    enabled: true
    # project_id - The ID of the project where this VPC will be created
    project_id: ""
    # network_name - The name of the network being created
    network_name: ""
  # dns: { internal: { … }, external: { … } }
gke:
  cluster:
    enabled: true
    # …
```

## Day-2 workflow

The scaffold's `.bashrc` wraps Terragrunt with environment-aware helpers.
Source it, pick an environment, then plan/apply a subtree:

```bash
source .bashrc            # adds switch_env / init / plan / apply / destroy / …
switch_env dev           # sets ENV=dev and `gcloud config set project`

plan  ./google/network   # terragrunt run-all plan on the whole network subtree
apply ./google/network/vpc
```

Because every module shares the root config and the single `config.<env>.yaml`,
adding a new environment is just a new `config.staging.yaml` and
`switch_env staging` — no module edits required.

## The full bootstrap script

The complete reference script — cookiecutter scaffold plus every
`terragrunt-generator` invocation — is reproduced below. Save it as
`bootstrap_gcp_infra.sh` and run it from an empty directory; it creates the
project, provisions a virtualenv, and writes the Terragrunt files. It does not
apply anything to your cloud account on its own.

```bash
#!/usr/bin/env bash

echo "build infra"

tmpfile=$(mktemp)
cat <<EOF > "$tmpfile"
default_context:
  full_name: "Chris"
  email: "goabonga@pm.me"
  github_username: "goabonga"
  project_name: "GCP Infrastructure"
  remote_state_bucket_name: ""
  default_environment: "dev"
EOF

uvx cookiecutter -f --no-input --config-file "$tmpfile" https://github.com/goabonga/cookiecutter-terragrunt-project.git

rm "$tmpfile"

cd gcp_infrastructure


uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-cloud-dns.git \
    -v v5.3.0 \
    -l network.dns.internal \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/dns/internal

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-cloud-dns.git \
    -v v5.3.0 \
    -l network.dns.external \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/dns/external

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-network.git \
    -v v10.0.0 \
    -l network.vpc \
    -p modules/vpc \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/vpc

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-network.git \
    -v v10.0.0 \
    -l network.subnets \
    -p modules/subnets-beta \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/subnets

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-network.git \
    -v v10.0.0 \
    -l network.firewall \
    -p modules/firewall-rules \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/firewall

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-network.git \
    -v v10.0.0 \
    -l network.routes \
    -p modules/routes-beta \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/routes

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-network.git \
    -v v10.0.0 \
    -l network.peering \
    -p modules/network-peering \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/peering

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-cloud-nat.git \
    -v v5.3.0 \
    -l network.nat \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/nat

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-address.git \
    -v v4.1.0 \
    -l network.address.internal \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/address/internal

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-address.git \
    -v v4.1.0 \
    -l network.address.external \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/network/address/external

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-kms.git \
    -v v4.0.0 \
    -l kms \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/kms

uvx terragrunt-generator \
    -u https://github.com/GoogleCloudPlatform/terraform-google-artifact-registry.git \
    -v v0.3.0 \
    -l registries.docker \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/registries/docker

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-cloud-storage.git \
    -v v10.0.1 \
    -l buckets \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/buckets

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-log-export.git \
    -v v10.0.0 \
    -l log.logexport \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/log/logexport

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-log-export.git \
    -v v10.0.0 \
    -l log.logbucket \
    -p modules/logbucket \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/log/logbucket

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-kubernetes-engine.git \
    -v v36.3.0 \
    -l gke.cluster \
    -p modules/beta-private-cluster-update-variant \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/gke/cluster

uvx terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-kubernetes-engine.git \
    -v v36.3.0 \
    -l gke.workload-identity \
    -p modules/workload-identity \
    --yaml-output ./ \
    --yaml-for-env dev \
    --output google/gke/workload-identity
```
