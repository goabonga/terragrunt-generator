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

```sh
$ terragrunt-generator -u https://github.com/terraform-google-modules/terraform-google-project-factory.git -v v14.2.1 -l 'project' | wl-copy
```

### Results

```hcl
# terraform-google-project-factory v14.2.1
# https://github.com/terraform-google-modules/terraform-google-project-factory/tree/v14.2.1/
#
# yaml config
# ```
# project:
#   enabled: true
#   # org_id - The organization ID.
#   org_id: 
#   # name - The name for the project
#   name: 
#   # billing_account - The ID of the billing account to associate this project with
#   billing_account: 
#   # random_project_id - Adds a suffix of 4 random characters to the `project_id`.
#   random_project_id: 
#   # domain - The domain name (optional).
#   domain: 
#   # project_id - The ID to give the project. If not provided, the `name` will be used.
#   project_id: 
#   # svpc_host_project_id - The ID of the host project which hosts the shared VPC
#   svpc_host_project_id: 
#   # enable_shared_vpc_host_project - If this project is a shared VPC host project. If true, you must *not* set svpc_host_project_id variable. Default is false.
#   enable_shared_vpc_host_project: 
#   # folder_id - The ID of a folder to host this project
#   folder_id: 
#   # group_name - A group to control the project by being assigned group_role (defaults to project editor)
#   group_name: 
#   # group_role - The role to give the controlling group (group_name) over the project (defaults to project editor)
#   group_role: "roles/editor"
#   # create_project_sa - Whether the default service account for the project shall be created
#   create_project_sa: true
#   # project_sa_name - Default service account name for the project.
#   project_sa_name: "project-service-account"
#   # sa_role - A role to give the default Service Account for the project (defaults to none)
#   sa_role: 
#   # activate_apis - The list of apis to activate within the project
#   activate_apis: ["compute.googleapis.com"]
#   # activate_api_identities - The list of service identities (Google Managed service account for the API) to force-create for the project (e.g. in order to grant additional roles).
#   #    APIs in this list will automatically be appended to `activate_apis`.
#   #    Not including the API in this list will follow the default behaviour for identity creation (which is usually when the first resource using the API is created).
#   #    Any roles (e.g. service agent role) must be explicitly listed. See https://cloud.google.com/iam/docs/understanding-roles#service-agent-roles-roles for a list of related roles.
#   activate_api_identities: 
#   # usage_bucket_name - Name of a GCS bucket to store GCE usage reports in (optional)
#   usage_bucket_name: 
#   # usage_bucket_prefix - Prefix in the GCS bucket to store GCE usage reports in (optional)
#   usage_bucket_prefix: 
#   # shared_vpc_subnets - List of subnets fully qualified subnet IDs (ie. projects/$project_id/regions/$region/subnetworks/$subnet_id)
#   shared_vpc_subnets: 
#   # labels - Map of labels for project
#   labels: 
#   # bucket_project - A project to create a GCS bucket (bucket_name) in, useful for Terraform state (optional)
#   bucket_project: 
#   # bucket_name - A name for a GCS bucket to create (in the bucket_project project), useful for Terraform state (optional)
#   bucket_name: 
#   # bucket_location - The location for a GCS bucket to create (optional)
#   bucket_location: "US"
#   # bucket_versioning - Enable versioning for a GCS bucket to create (optional)
#   bucket_versioning: 
#   # bucket_labels -  A map of key/value label pairs to assign to the bucket (optional)
#   bucket_labels: 
#   # bucket_force_destroy - Force the deletion of all objects within the GCS bucket when deleting the bucket (optional)
#   bucket_force_destroy: 
#   # bucket_ula - Enable Uniform Bucket Level Access
#   bucket_ula: true
#   # bucket_pap - Enable Public Access Prevention. Possible values are "enforced" or "inherited".
#   bucket_pap: "inherited"
#   # auto_create_network - Create the default network
#   auto_create_network: 
#   # lien - Add a lien on the project to prevent accidental deletion
#   lien: 
#   # disable_services_on_destroy - Whether project services will be disabled when the resources are destroyed
#   disable_services_on_destroy: true
#   # default_service_account - Project default service account setting: can be one of `delete`, `deprivilege`, `disable`, or `keep`.
#   default_service_account: "disable"
#   # disable_dependent_services - Whether services that are enabled and which depend on this service should also be disabled when this service is destroyed.
#   disable_dependent_services: true
#   # budget_monitoring_notification_channels - A list of monitoring notification channels in the form `[projects/{project_id}/notificationChannels/{channel_id}]`. A maximum of 5 channels are allowed.
#   budget_monitoring_notification_channels: 
#   # budget_alert_spent_percents - A list of percentages of the budget to alert on when threshold is exceeded
#   budget_alert_spent_percents: [0.5, 0.7, 1.0]
#   # budget_alert_spend_basis - The type of basis used to determine if spend has passed the threshold
#   budget_alert_spend_basis: "CURRENT_SPEND"
#   # budget_labels - A single label and value pair specifying that usage from only this set of labeled resources should be included in the budget.
#   budget_labels: 
#   # vpc_service_control_attach_enabled - Whether the project will be attached to a VPC Service Control Perimeter
#   vpc_service_control_attach_enabled: 
#   # vpc_service_control_sleep_duration - The duration to sleep in seconds before adding the project to a shared VPC after the project is added to the VPC Service Control Perimeter. VPC-SC is eventually consistent.
#   vpc_service_control_sleep_duration: "5s"
#   # grant_services_security_admin_role - Whether or not to grant Kubernetes Engine Service Agent the Security Admin role on the host project so it can manage firewall rules
#   grant_services_security_admin_role: 
#   # grant_network_role - Whether or not to grant networkUser role on the host project/subnets
#   grant_network_role: true
#   # consumer_quotas - The quotas configuration you want to override for the project.
#   consumer_quotas: 
#   # default_network_tier - Default Network Service Tier for resources created in this project. If unset, the value will not be modified. See https://cloud.google.com/network-tiers/docs/using-network-service-tiers and https://cloud.google.com/network-tiers.
#   default_network_tier: 
#   # essential_contacts - A mapping of users or groups to be assigned as Essential Contacts to the project, specifying a notification category
#   essential_contacts: 
#   # language_tag - Language code to be used for essential contacts notifications
#   language_tag: "en-US"
#   # random_project_id_length - Sets the length of `random_project_id` to the provided length, and uses a `random_string` for a larger collusion domain.  Recommended for use with CI.
#   # random_project_id_length: 
#   # budget_amount - The amount to use for a budget alert
#   # budget_amount: 
#   # budget_display_name - The display name of the budget. If not set defaults to `Budget For <projects[0]|All Projects>` 
#   # budget_display_name: 
#   # budget_alert_pubsub_topic - The name of the Cloud Pub/Sub topic where budget related messages will be published, in the form of `projects/{project_id}/topics/{topic_id}`
#   # budget_alert_pubsub_topic: 
#   # budget_calendar_period - Specifies the calendar period for the budget. Possible values are MONTH, QUARTER, YEAR, CALENDAR_PERIOD_UNSPECIFIED, CUSTOM. custom_period_start_date and custom_period_end_date must be set if CUSTOM
#   # budget_calendar_period: 
#   # budget_custom_period_start_date - Specifies the start date (DD-MM-YYYY) for the calendar_period CUSTOM
#   # budget_custom_period_start_date: 
#   # budget_custom_period_end_date - Specifies the end date (DD-MM-YYYY) for the calendar_period CUSTOM
#   # budget_custom_period_end_date: 
#   # vpc_service_control_perimeter_name - The name of a VPC Service Control Perimeter to add the created project to
#   # vpc_service_control_perimeter_name: 
# ```
#

include {
    path = find_in_parent_folders()
}

locals {
    module = {
        repository = "github.com/terraform-google-modules/terraform-google-project-factory.git"
        path = null
        version = "v14.2.1"
        source =  "${local.module.repository}${local.module.path != null ? local.module.path : ''}?ref=${local.module.version}"
    }
    environment = get_env("ENV", "development")
    all = merge(
        yamldecode(file(find_in_parent_folders(format("config.%s.yaml", local.environment)))),
    )
}

terraform {
    source = lookup(project, "enabled", true) == true ? local.module.source : null
}

inputs = merge({
    # billing_account - The ID of the billing account to associate this project with - required
    billing_account = lookup(project, "billing_account", "")
    # name - The name for the project - required
    name = lookup(project, "name", "")
    # org_id - The organization ID. - required
    org_id = lookup(project, "org_id", "")
    # activate_api_identities - The list of service identities (Google Managed service account for the API) to force-create for the project (e.g. in order to grant additional roles).
    # APIs in this list will automatically be appended to `activate_apis`.
    # Not including the API in this list will follow the default behaviour for identity creation (which is usually when the first resource using the API is created).
    # Any roles (e.g. service agent role) must be explicitly listed. See https://cloud.google.com/iam/docs/understanding-roles#service-agent-roles-roles for a list of related roles.
    activate_api_identities = lookup(project, "activate_api_identities", [])
    # activate_apis - The list of apis to activate within the project
    activate_apis = lookup(project, "activate_apis", ["compute.googleapis.com"])
    # auto_create_network - Create the default network
    auto_create_network = lookup(project, "auto_create_network", false)
    # bucket_force_destroy - Force the deletion of all objects within the GCS bucket when deleting the bucket (optional)
    bucket_force_destroy = lookup(project, "bucket_force_destroy", false)
    # bucket_labels -  A map of key/value label pairs to assign to the bucket (optional)
    bucket_labels = lookup(project, "bucket_labels", {})
    # bucket_location - The location for a GCS bucket to create (optional)
    bucket_location = lookup(project, "bucket_location", "US")
    # bucket_name - A name for a GCS bucket to create (in the bucket_project project), useful for Terraform state (optional)
    bucket_name = lookup(project, "bucket_name", "")
    # bucket_pap - Enable Public Access Prevention. Possible values are "enforced" or "inherited".
    bucket_pap = lookup(project, "bucket_pap", "inherited")
    # bucket_project - A project to create a GCS bucket (bucket_name) in, useful for Terraform state (optional)
    bucket_project = lookup(project, "bucket_project", "")
    # bucket_ula - Enable Uniform Bucket Level Access
    bucket_ula = lookup(project, "bucket_ula", true)
    # bucket_versioning - Enable versioning for a GCS bucket to create (optional)
    bucket_versioning = lookup(project, "bucket_versioning", false)
    # budget_alert_spend_basis - The type of basis used to determine if spend has passed the threshold
    budget_alert_spend_basis = lookup(project, "budget_alert_spend_basis", "CURRENT_SPEND")
    # budget_alert_spent_percents - A list of percentages of the budget to alert on when threshold is exceeded
    budget_alert_spent_percents = lookup(project, "budget_alert_spent_percents", [0.5, 0.7, 1.0])
    # budget_labels - A single label and value pair specifying that usage from only this set of labeled resources should be included in the budget.
    budget_labels = lookup(project, "budget_labels", {})
    # budget_monitoring_notification_channels - A list of monitoring notification channels in the form `[projects/{project_id}/notificationChannels/{channel_id}]`. A maximum of 5 channels are allowed.
    budget_monitoring_notification_channels = lookup(project, "budget_monitoring_notification_channels", [])
    # consumer_quotas - The quotas configuration you want to override for the project.
    consumer_quotas = lookup(project, "consumer_quotas", [])
    # create_project_sa - Whether the default service account for the project shall be created
    create_project_sa = lookup(project, "create_project_sa", true)
    # default_network_tier - Default Network Service Tier for resources created in this project. If unset, the value will not be modified. See https://cloud.google.com/network-tiers/docs/using-network-service-tiers and https://cloud.google.com/network-tiers.
    default_network_tier = lookup(project, "default_network_tier", "")
    # default_service_account - Project default service account setting: can be one of `delete`, `deprivilege`, `disable`, or `keep`.
    default_service_account = lookup(project, "default_service_account", "disable")
    # disable_dependent_services - Whether services that are enabled and which depend on this service should also be disabled when this service is destroyed.
    disable_dependent_services = lookup(project, "disable_dependent_services", true)
    # disable_services_on_destroy - Whether project services will be disabled when the resources are destroyed
    disable_services_on_destroy = lookup(project, "disable_services_on_destroy", true)
    # domain - The domain name (optional).
    domain = lookup(project, "domain", "")
    # enable_shared_vpc_host_project - If this project is a shared VPC host project. If true, you must *not* set svpc_host_project_id variable. Default is false.
    enable_shared_vpc_host_project = lookup(project, "enable_shared_vpc_host_project", false)
    # essential_contacts - A mapping of users or groups to be assigned as Essential Contacts to the project, specifying a notification category
    essential_contacts = lookup(project, "essential_contacts", {})
    # folder_id - The ID of a folder to host this project
    folder_id = lookup(project, "folder_id", "")
    # grant_network_role - Whether or not to grant networkUser role on the host project/subnets
    grant_network_role = lookup(project, "grant_network_role", true)
    # grant_services_security_admin_role - Whether or not to grant Kubernetes Engine Service Agent the Security Admin role on the host project so it can manage firewall rules
    grant_services_security_admin_role = lookup(project, "grant_services_security_admin_role", false)
    # group_name - A group to control the project by being assigned group_role (defaults to project editor)
    group_name = lookup(project, "group_name", "")
    # group_role - The role to give the controlling group (group_name) over the project (defaults to project editor)
    group_role = lookup(project, "group_role", "roles/editor")
    # labels - Map of labels for project
    labels = lookup(project, "labels", {})
    # language_tag - Language code to be used for essential contacts notifications
    language_tag = lookup(project, "language_tag", "en-US")
    # lien - Add a lien on the project to prevent accidental deletion
    lien = lookup(project, "lien", false)
    # project_id - The ID to give the project. If not provided, the `name` will be used.
    project_id = lookup(project, "project_id", "")
    # project_sa_name - Default service account name for the project.
    project_sa_name = lookup(project, "project_sa_name", "project-service-account")
    # random_project_id - Adds a suffix of 4 random characters to the `project_id`.
    random_project_id = lookup(project, "random_project_id", false)
    # sa_role - A role to give the default Service Account for the project (defaults to none)
    sa_role = lookup(project, "sa_role", "")
    # shared_vpc_subnets - List of subnets fully qualified subnet IDs (ie. projects/$project_id/regions/$region/subnetworks/$subnet_id)
    shared_vpc_subnets = lookup(project, "shared_vpc_subnets", [])
    # svpc_host_project_id - The ID of the host project which hosts the shared VPC
    svpc_host_project_id = lookup(project, "svpc_host_project_id", "")
    # usage_bucket_name - Name of a GCS bucket to store GCE usage reports in (optional)
    usage_bucket_name = lookup(project, "usage_bucket_name", "")
    # usage_bucket_prefix - Prefix in the GCS bucket to store GCE usage reports in (optional)
    usage_bucket_prefix = lookup(project, "usage_bucket_prefix", "")
    # vpc_service_control_attach_enabled - Whether the project will be attached to a VPC Service Control Perimeter
    vpc_service_control_attach_enabled = lookup(project, "vpc_service_control_attach_enabled", false)
    # vpc_service_control_sleep_duration - The duration to sleep in seconds before adding the project to a shared VPC after the project is added to the VPC Service Control Perimeter. VPC-SC is eventually consistent.
    vpc_service_control_sleep_duration = lookup(project, "vpc_service_control_sleep_duration", "5s")
},
  # budget_alert_pubsub_topic - The name of the Cloud Pub/Sub topic where budget related messages will be published, in the form of `projects/{project_id}/topics/{topic_id}`
  (lookup(project, "budget_alert_pubsub_topic", null) == null ? {} : { budget_alert_pubsub_topic =  lookup(project, "budget_alert_pubsub_topic") }),
  # budget_amount - The amount to use for a budget alert
  (lookup(project, "budget_amount", null) == null ? {} : { budget_amount =  lookup(project, "budget_amount") }),
  # budget_calendar_period - Specifies the calendar period for the budget. Possible values are MONTH, QUARTER, YEAR, CALENDAR_PERIOD_UNSPECIFIED, CUSTOM. custom_period_start_date and custom_period_end_date must be set if CUSTOM
  (lookup(project, "budget_calendar_period", null) == null ? {} : { budget_calendar_period =  lookup(project, "budget_calendar_period") }),
  # budget_custom_period_end_date - Specifies the end date (DD-MM-YYYY) for the calendar_period CUSTOM
  (lookup(project, "budget_custom_period_end_date", null) == null ? {} : { budget_custom_period_end_date =  lookup(project, "budget_custom_period_end_date") }),
  # budget_custom_period_start_date - Specifies the start date (DD-MM-YYYY) for the calendar_period CUSTOM
  (lookup(project, "budget_custom_period_start_date", null) == null ? {} : { budget_custom_period_start_date =  lookup(project, "budget_custom_period_start_date") }),
  # budget_display_name - The display name of the budget. If not set defaults to `Budget For <projects[0]|All Projects>` 
  (lookup(project, "budget_display_name", null) == null ? {} : { budget_display_name =  lookup(project, "budget_display_name") }),
  # random_project_id_length - Sets the length of `random_project_id` to the provided length, and uses a `random_string` for a larger collusion domain.  Recommended for use with CI.
  (lookup(project, "random_project_id_length", null) == null ? {} : { random_project_id_length =  lookup(project, "random_project_id_length") }),
  # vpc_service_control_perimeter_name - The name of a VPC Service Control Perimeter to add the created project to
  (lookup(project, "vpc_service_control_perimeter_name", null) == null ? {} : { vpc_service_control_perimeter_name =  lookup(project, "vpc_service_control_perimeter_name") })
)
```
