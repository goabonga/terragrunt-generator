# terragrunt-generator

**terragrunt-generator** provide a way to generate a ```terragrunt.hcl``` file with documented inputs who's comming from variables exposed by terraform module.

The result is easily configurable with a **yaml** file.
## Requirements

- python3.6+

## Instalation

```
$ pip install terragrunt-generator
```

## Example

```
$ terragrunt-generator -u https://github.com/terraform-google-modules/terraform-google-project-factory.git -v v13.1.0
# terraform-google-project-factory v13.1.0
#
# yaml config
# ```
# terraform-google-project-factory:
#   enabled: true
#   random_project_id: false
#   org_id:
#   domain: ""
#   name:
#   project_id: ""
#   svpc_host_project_id: ""
#   enable_shared_vpc_host_project: false
#   billing_account:
#   folder_id: ""
#   group_name: ""
#   group_role: "roles/editor"
#   create_project_sa: true
#   project_sa_name: "project-service-account"
#   sa_role: ""
#   activate_apis: ["compute.googleapis.com"]
#   activate_api_identities: []
#   usage_bucket_name: ""
#   usage_bucket_prefix: ""
#   shared_vpc_subnets: []
#   labels: {}
#   bucket_project: ""
#   bucket_name: ""
#   bucket_location: "US"
#   bucket_versioning: false
#   bucket_labels: {}
#   bucket_force_destroy: false
#   bucket_ula: true
#   bucket_pap: "inherited"
#   auto_create_network: false
#   lien: false
#   disable_services_on_destroy: true
#   default_service_account: "disable"
#   disable_dependent_services: true
#   budget_amount:
#   budget_display_name:
#   budget_alert_pubsub_topic:
#   budget_monitoring_notification_channels: []
#   budget_alert_spent_percents: [0.5, 0.7, 1.0]
#   budget_alert_spend_basis: "CURRENT_SPEND"
#   budget_labels: {}
#   vpc_service_control_attach_enabled: false
#   vpc_service_control_perimeter_name:
#   grant_services_security_admin_role: false
#   grant_network_role: true
#   consumer_quotas: []
#   default_network_tier: ""
#   essential_contacts: {}
#   language_tag: "en-US"
# ```
#
include {
    path = "${{find_in_parent_folders()}}"
}

locals {
    all = merge(
        yamldecode(file(find_in_parent_folders("config.yaml"))),
    )
}

terraform {
    source = lookup(local.all["terraform-google-project-factory"], "enabled", true) == true ? "https://github.com/terraform-google-modules/terraform-google-project-factory.git?ref=v13.1.0" : null
}

inputs = merge({
    # billing_account - The ID of the billing account to associate this project with - required
    billing_account = lookup(local.all["terraform-google-project-factory"], "billing_account", "None")
    # name - The name for the project - required
    name = lookup(local.all["terraform-google-project-factory"], "name", "None")
    # org_id - The organization ID. - required
    org_id = lookup(local.all["terraform-google-project-factory"], "org_id", "None")
    # activate_api_identities - The list of service identities (Google Managed service account for the API) to force-create for the project (e.g. in order to grant additional roles).
    #    APIs in this list will automatically be appended to `activate_apis`.
    #    Not including the API in this list will follow the default behaviour for identity creation (which is usually when the first resource using the API is created).
    #    Any roles (e.g. service agent role) must be explicitly listed. See https://cloud.google.com/iam/docs/understanding-roles#service-agent-roles-roles for a list of related roles.
    activate_api_identities = lookup(local.all["terraform-google-project-factory"], "activate_api_identities", [])
    # activate_apis - The list of apis to activate within the project
    activate_apis = lookup(local.all["terraform-google-project-factory"], "activate_apis", ["compute.googleapis.com"])
    # auto_create_network - Create the default network
    auto_create_network = lookup(local.all["terraform-google-project-factory"], "auto_create_network", false)
    # bucket_force_destroy - Force the deletion of all objects within the GCS bucket when deleting the bucket (optional)
    bucket_force_destroy = lookup(local.all["terraform-google-project-factory"], "bucket_force_destroy", false)
    # bucket_labels -  A map of key/value label pairs to assign to the bucket (optional)
    bucket_labels = lookup(local.all["terraform-google-project-factory"], "bucket_labels", {})
    # bucket_location - The location for a GCS bucket to create (optional)
    bucket_location = lookup(local.all["terraform-google-project-factory"], "bucket_location", "US")
    # bucket_name - A name for a GCS bucket to create (in the bucket_project project), useful for Terraform state (optional)
    bucket_name = lookup(local.all["terraform-google-project-factory"], "bucket_name", "")
    # bucket_pap - Enable Public Access Prevention. Possible values are "enforced" or "inherited".
    bucket_pap = lookup(local.all["terraform-google-project-factory"], "bucket_pap", "inherited")
    # bucket_project - A project to create a GCS bucket (bucket_name) in, useful for Terraform state (optional)
    bucket_project = lookup(local.all["terraform-google-project-factory"], "bucket_project", "")
    # bucket_ula - Enable Uniform Bucket Level Access
    bucket_ula = lookup(local.all["terraform-google-project-factory"], "bucket_ula", true)
    # bucket_versioning - Enable versioning for a GCS bucket to create (optional)
    bucket_versioning = lookup(local.all["terraform-google-project-factory"], "bucket_versioning", false)
    # budget_alert_spend_basis - The type of basis used to determine if spend has passed the threshold
    budget_alert_spend_basis = lookup(local.all["terraform-google-project-factory"], "budget_alert_spend_basis", "CURRENT_SPEND")
    # budget_alert_spent_percents - A list of percentages of the budget to alert on when threshold is exceeded
    budget_alert_spent_percents = lookup(local.all["terraform-google-project-factory"], "budget_alert_spent_percents", [0.5, 0.7, 1.0])
    # budget_labels - A single label and value pair specifying that usage from only this set of labeled resources should be included in the budget.
    budget_labels = lookup(local.all["terraform-google-project-factory"], "budget_labels", {})
    # budget_monitoring_notification_channels - A list of monitoring notification channels in the form `[projects/{project_id}/notificationChannels/{channel_id}]`. A maximum of 5 channels are allowed.
    budget_monitoring_notification_channels = lookup(local.all["terraform-google-project-factory"], "budget_monitoring_notification_channels", [])
    # consumer_quotas - The quotas configuration you want to override for the project.
    consumer_quotas = lookup(local.all["terraform-google-project-factory"], "consumer_quotas", [])
    # create_project_sa - Whether the default service account for the project shall be created
    create_project_sa = lookup(local.all["terraform-google-project-factory"], "create_project_sa", true)
    # default_network_tier - Default Network Service Tier for resources created in this project. If unset, the value will not be modified. See https://cloud.google.com/network-tiers/docs/using-network-service-tiers and https://cloud.google.com/network-tiers.
    default_network_tier = lookup(local.all["terraform-google-project-factory"], "default_network_tier", "")
    # default_service_account - Project default service account setting: can be one of `delete`, `deprivilege`, `disable`, or `keep`.
    default_service_account = lookup(local.all["terraform-google-project-factory"], "default_service_account", "disable")
    # disable_dependent_services - Whether services that are enabled and which depend on this service should also be disabled when this service is destroyed.
    disable_dependent_services = lookup(local.all["terraform-google-project-factory"], "disable_dependent_services", true)
    # disable_services_on_destroy - Whether project services will be disabled when the resources are destroyed
    disable_services_on_destroy = lookup(local.all["terraform-google-project-factory"], "disable_services_on_destroy", true)
    # domain - The domain name (optional).
    domain = lookup(local.all["terraform-google-project-factory"], "domain", "")
    # enable_shared_vpc_host_project - If this project is a shared VPC host project. If true, you must *not* set svpc_host_project_id variable. Default is false.
    enable_shared_vpc_host_project = lookup(local.all["terraform-google-project-factory"], "enable_shared_vpc_host_project", false)
    # essential_contacts - A mapping of users or groups to be assigned as Essential Contacts to the project, specifying a notification category
    essential_contacts = lookup(local.all["terraform-google-project-factory"], "essential_contacts", {})
    # folder_id - The ID of a folder to host this project
    folder_id = lookup(local.all["terraform-google-project-factory"], "folder_id", "")
    # grant_network_role - Whether or not to grant networkUser role on the host project/subnets
    grant_network_role = lookup(local.all["terraform-google-project-factory"], "grant_network_role", true)
    # grant_services_security_admin_role - Whether or not to grant Kubernetes Engine Service Agent the Security Admin role on the host project so it can manage firewall rules
    grant_services_security_admin_role = lookup(local.all["terraform-google-project-factory"], "grant_services_security_admin_role", false)
    # group_name - A group to control the project by being assigned group_role (defaults to project editor)
    group_name = lookup(local.all["terraform-google-project-factory"], "group_name", "")
    # group_role - The role to give the controlling group (group_name) over the project (defaults to project editor)
    group_role = lookup(local.all["terraform-google-project-factory"], "group_role", "roles/editor")
    # labels - Map of labels for project
    labels = lookup(local.all["terraform-google-project-factory"], "labels", {})
    # language_tag - Language code to be used for essential contacts notifications
    language_tag = lookup(local.all["terraform-google-project-factory"], "language_tag", "en-US")
    # lien - Add a lien on the project to prevent accidental deletion
    lien = lookup(local.all["terraform-google-project-factory"], "lien", false)
    # project_id - The ID to give the project. If not provided, the `name` will be used.
    project_id = lookup(local.all["terraform-google-project-factory"], "project_id", "")
    # project_sa_name - Default service account name for the project.
    project_sa_name = lookup(local.all["terraform-google-project-factory"], "project_sa_name", "project-service-account")
    # random_project_id - Adds a suffix of 4 random characters to the `project_id`
    random_project_id = lookup(local.all["terraform-google-project-factory"], "random_project_id", false)
    # sa_role - A role to give the default Service Account for the project (defaults to none)
    sa_role = lookup(local.all["terraform-google-project-factory"], "sa_role", "")
    # shared_vpc_subnets - List of subnets fully qualified subnet IDs (ie. projects/$project_id/regions/$region/subnetworks/$subnet_id)
    shared_vpc_subnets = lookup(local.all["terraform-google-project-factory"], "shared_vpc_subnets", [])
    # svpc_host_project_id - The ID of the host project which hosts the shared VPC
    svpc_host_project_id = lookup(local.all["terraform-google-project-factory"], "svpc_host_project_id", "")
    # usage_bucket_name - Name of a GCS bucket to store GCE usage reports in (optional)
    usage_bucket_name = lookup(local.all["terraform-google-project-factory"], "usage_bucket_name", "")
    # usage_bucket_prefix - Prefix in the GCS bucket to store GCE usage reports in (optional)
    usage_bucket_prefix = lookup(local.all["terraform-google-project-factory"], "usage_bucket_prefix", "")
    # vpc_service_control_attach_enabled - Whether the project will be attached to a VPC Service Control Perimeter
    vpc_service_control_attach_enabled = lookup(local.all["terraform-google-project-factory"], "vpc_service_control_attach_enabled", false)

},
  # budget_alert_pubsub_topic - Enable versioning for a GCS bucket to create (optional)
  (lookup(local.all["terraform-google-project-factory"], "budget_alert_pubsub_topic", null) == null ? {} : { budget_alert_pubsub_topic =  lookup(local.all["terraform-google-project-factory"], "budget_alert_pubsub_topic") }),
  # budget_amount - A list of percentages of the budget to alert on when threshold is exceeded
  (lookup(local.all["terraform-google-project-factory"], "budget_amount", null) == null ? {} : { budget_amount =  lookup(local.all["terraform-google-project-factory"], "budget_amount") }),
  # budget_display_name - A list of percentages of the budget to alert on when threshold is exceeded
  (lookup(local.all["terraform-google-project-factory"], "budget_display_name", null) == null ? {} : { budget_display_name =  lookup(local.all["terraform-google-project-factory"], "budget_display_name") }),
  # vpc_service_control_perimeter_name - Whether the project will be attached to a VPC Service Control Perimeter
  (lookup(local.all["terraform-google-project-factory"], "vpc_service_control_perimeter_name", null) == null ? {} : { vpc_service_control_perimeter_name =  lookup(local.all["terraform-google-project-factory"], "vpc_service_control_perimeter_name") })
)

```
