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
$ terragrunt-generator \
    -u https://github.com/terraform-google-modules/terraform-google-kubernetes-engine.git \
    -v v25.0.0 \
    -p modules/beta-private-cluster-update-variant
```

### Results

```hcl
# beta-private-cluster-update-variant v25.0.0
# https://github.com/terraform-google-modules/terraform-google-kubernetes-engine/tree/v25.0.0/modules/beta-private-cluster-update-variant
#
# yaml config
# ```
# beta-private-cluster-update-variant:
#   enabled: true
#   # project_id - The project ID to host the cluster in (required)
#   project_id:
#   # name - The name of the cluster (required)
#   name:
#   # network - The VPC network to host the cluster in (required)
#   network:
#   # subnetwork - The subnetwork to host the cluster in (required)
#   subnetwork:
#   # ip_range_pods - The _name_ of the secondary subnet ip range to use for pods
#   ip_range_pods:
#   # ip_range_services - The _name_ of the secondary subnet range to use for services
#   ip_range_services:
#   # description - The description of the cluster
#   description:
#   # regional - Whether is a regional cluster (zonal cluster if set false. WARNING: changing this after cluster creation is destructive!)
#   regional: true
#   # zones - The zones to host the cluster in (optional if regional cluster / required if zonal)
#   zones:
#   # network_project_id - The project ID of the shared VPC's host (for shared vpc support)
#   network_project_id:
#   # kubernetes_version - The Kubernetes version of the masters. If set to 'latest' it will pull latest available version in the selected region.
#   kubernetes_version: "latest"
#   # master_authorized_networks - List of master authorized networks. If none are provided, disallow external access (except the cluster node IPs, which GKE automatically whitelists).
#   master_authorized_networks:
#   # enable_vertical_pod_autoscaling - Vertical Pod Autoscaling automatically adjusts the resources of pods controlled by it
#   enable_vertical_pod_autoscaling:
#   # horizontal_pod_autoscaling - Enable horizontal pod autoscaling addon
#   horizontal_pod_autoscaling: true
#   # http_load_balancing - Enable httpload balancer addon
#   http_load_balancing: true
#   # service_external_ips - Whether external ips specified by a service will be allowed in this cluster
#   service_external_ips:
#   # datapath_provider - The desired datapath provider for this cluster. By default, `DATAPATH_PROVIDER_UNSPECIFIED` enables the IPTables-based kube-proxy implementation. `ADVANCED_DATAPATH` enables Dataplane-V2 feature.
#   datapath_provider: "DATAPATH_PROVIDER_UNSPECIFIED"
#   # maintenance_start_time - Time window specified for daily or recurring maintenance operations in RFC3339 format
#   maintenance_start_time: "05:00"
#   # maintenance_exclusions - List of maintenance exclusions. A cluster can have up to three
#   maintenance_exclusions:
#   # maintenance_end_time - Time window specified for recurring maintenance operations in RFC3339 format
#   maintenance_end_time:
#   # maintenance_recurrence - Frequency of the recurring maintenance window in RFC5545 format.
#   maintenance_recurrence:
#   # node_pools - List of maps containing node pools
#   node_pools: [{"name": "default-node-pool"}]
#   # windows_node_pools - List of maps containing Windows node pools
#   windows_node_pools:
#   # node_pools_labels - Map of maps containing node labels by node-pool name
#   node_pools_labels: {"all": {}, "default-node-pool": {}}
#   # node_pools_resource_labels - Map of maps containing resource labels by node-pool name
#   node_pools_resource_labels: {"all": {}, "default-node-pool": {}}
#   # node_pools_metadata - Map of maps containing node metadata by node-pool name
#   node_pools_metadata: {"all": {}, "default-node-pool": {}}
#   # node_pools_linux_node_configs_sysctls - Map of maps containing linux node config sysctls by node-pool name
#   node_pools_linux_node_configs_sysctls: {"all": {}, "default-node-pool": {}}
#   # enable_cost_allocation - Enables Cost Allocation Feature and the cluster name and namespace of your GKE workloads appear in the labels field of the billing export to BigQuery
#   enable_cost_allocation:
#   # resource_usage_export_dataset_id - The ID of a BigQuery Dataset for using BigQuery as the destination of resource usage export.
#   resource_usage_export_dataset_id:
#   # enable_network_egress_export - Whether to enable network egress metering for this cluster. If enabled, a daemonset will be created in the cluster to meter network egress traffic.
#   enable_network_egress_export:
#   # enable_resource_consumption_export - Whether to enable resource consumption metering on this cluster. When enabled, a table will be created in the resource export BigQuery dataset to store resource consumption data. The resulting table can be joined with the resource usage table or with BigQuery billing export.
#   enable_resource_consumption_export: true
#   # cluster_autoscaling - Cluster autoscaling configuration. See [more details](https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1beta1/projects.locations.clusters#clusterautoscaling)
#   cluster_autoscaling: {"enabled": false, "autoscaling_profile": "BALANCED", "max_cpu_cores": 0, "min_cpu_cores": 0, "max_memory_gb": 0, "min_memory_gb": 0, "gpu_resources": [], "auto_repair": true, "auto_upgrade": true}
#   # node_pools_taints - Map of lists containing node taints by node-pool name
#   node_pools_taints: {"all": [], "default-node-pool": []}
#   # node_pools_tags - Map of lists containing node network tags by node-pool name
#   node_pools_tags: {"all": [], "default-node-pool": []}
#   # node_pools_oauth_scopes - Map of lists containing node oauth scopes by node-pool name
#   node_pools_oauth_scopes: {"all": ["https://www.googleapis.com/auth/cloud-platform"], "default-node-pool": []}
#   # stub_domains - Map of stub domains and their resolvers to forward DNS queries for a certain domain to an external DNS server
#   stub_domains:
#   # upstream_nameservers - If specified, the values replace the nameservers taken by default from the node’s /etc/resolv.conf
#   upstream_nameservers:
#   # non_masquerade_cidrs - List of strings in CIDR notation that specify the IP address ranges that do not use IP masquerading.
#   non_masquerade_cidrs: ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
#   # ip_masq_resync_interval - The interval at which the agent attempts to sync its ConfigMap file from the disk.
#   ip_masq_resync_interval: "60s"
#   # ip_masq_link_local - Whether to masquerade traffic to the link-local prefix (169.254.0.0/16).
#   ip_masq_link_local:
#   # configure_ip_masq - Enables the installation of ip masquerading, which is usually no longer required when using aliasied IP addresses. IP masquerading uses a kubectl call, so when you have a private cluster, you will need access to the API server.
#   configure_ip_masq:
#   # logging_service - The logging service that the cluster should write logs to. Available options include logging.googleapis.com, logging.googleapis.com/kubernetes (beta), and none
#   logging_service: "logging.googleapis.com/kubernetes"
#   # monitoring_service - The monitoring service that the cluster should write metrics to. Automatically send metrics from pods in the cluster to the Google Cloud Monitoring API. VM metrics will be collected by Google Compute Engine regardless of this setting Available options include monitoring.googleapis.com, monitoring.googleapis.com/kubernetes (beta) and none
#   monitoring_service: "monitoring.googleapis.com/kubernetes"
#   # create_service_account - Defines if service account specified to run nodes should be created.
#   create_service_account: true
#   # grant_registry_access - Grants created cluster-specific service account storage.objectViewer and artifactregistry.reader roles.
#   grant_registry_access:
#   # registry_project_ids - Projects holding Google Container Registries. If empty, we use the cluster project. If a service account is created and the `grant_registry_access` variable is set to `true`, the `storage.objectViewer` and `artifactregsitry.reader` roles are assigned on these projects.
#   registry_project_ids:
#   # service_account - The service account to run nodes as if not overridden in `node_pools`. The create_service_account variable default value (true) will cause a cluster-specific service account to be created.
#   service_account:
#   # issue_client_certificate - Issues a client certificate to authenticate to the cluster endpoint. To maximize the security of your cluster, leave this option disabled. Client certificates don't automatically rotate and aren't easily revocable. WARNING: changing this after cluster creation is destructive!
#   issue_client_certificate:
#   # cluster_resource_labels - The GCE resource labels (a map of key/value pairs) to be applied to the cluster
#   cluster_resource_labels:
#   # skip_provisioners - Flag to skip all local-exec provisioners. It breaks `stub_domains` and `upstream_nameservers` variables functionality.
#   skip_provisioners:
#   # deploy_using_private_endpoint - (Beta) A toggle for Terraform and kubectl to connect to the master's internal IP address during deployment.
#   deploy_using_private_endpoint:
#   # enable_private_endpoint - (Beta) Whether the master's internal IP address is used as the cluster endpoint
#   enable_private_endpoint:
#   # enable_private_nodes - (Beta) Whether nodes have internal IP addresses only
#   enable_private_nodes:
#   # master_ipv4_cidr_block - (Beta) The IP range in CIDR notation to use for the hosted master network
#   master_ipv4_cidr_block: "10.0.0.0/28"
#   # master_global_access_enabled - Whether the cluster master is accessible globally (from any region) or only within the same region as the private endpoint.
#   master_global_access_enabled: true
#   # dns_cache - The status of the NodeLocal DNSCache addon.
#   dns_cache:
#   # identity_namespace - The workload pool to attach all Kubernetes service accounts to. (Default value of `enabled` automatically sets project-based pool `[project_id].svc.id.goog`)
#   identity_namespace: "enabled"
#   # add_cluster_firewall_rules - Create additional firewall rules
#   add_cluster_firewall_rules:
#   # add_master_webhook_firewall_rules - Create master_webhook firewall rules for ports defined in `firewall_inbound_ports`
#   add_master_webhook_firewall_rules:
#   # firewall_priority - Priority rule for firewall rules
#   firewall_priority: 1000
#   # firewall_inbound_ports - List of TCP ports for admission/webhook controllers. Either flag `add_master_webhook_firewall_rules` or `add_cluster_firewall_rules` (also adds egress rules) must be set to `true` for inbound-ports firewall rules to be applied.
#   firewall_inbound_ports: ["8443", "9443", "15017"]
#   # add_shadow_firewall_rules - Create GKE shadow firewall (the same as default firewall rules with firewall logs enabled).
#   add_shadow_firewall_rules:
#   # shadow_firewall_rules_priority - The firewall priority of GKE shadow firewall rules. The priority should be less than default firewall, which is 1000.
#   shadow_firewall_rules_priority: 999
#   # shadow_firewall_rules_log_config - The log_config for shadow firewall rules. You can set this variable to `null` to disable logging.
#   shadow_firewall_rules_log_config: {"metadata": "INCLUDE_ALL_METADATA"}
#   # enable_confidential_nodes - An optional flag to enable confidential node config.
#   enable_confidential_nodes:
#   # disable_default_snat - Whether to disable the default SNAT to support the private use of public IP addresses
#   disable_default_snat:
#   # notification_config_topic - The desired Pub/Sub topic to which notifications will be sent by GKE. Format is projects/{project}/topics/{topic}.
#   notification_config_topic:
#   # enable_tpu - Enable Cloud TPU resources in the cluster. WARNING: changing this after cluster creation is destructive!
#   enable_tpu:
#   # network_policy - Enable network policy addon
#   network_policy:
#   # network_policy_provider - The network policy provider.
#   network_policy_provider: "CALICO"
#   # initial_node_count - The number of nodes to create in this cluster's default node pool.
#   initial_node_count:
#   # remove_default_node_pool - Remove default node pool while setting up the cluster
#   remove_default_node_pool:
#   # filestore_csi_driver - The status of the Filestore CSI driver addon, which allows the usage of filestore instance as volumes
#   filestore_csi_driver:
#   # disable_legacy_metadata_endpoints - Disable the /0.1/ and /v1beta1/ metadata server endpoints on the node. Changing this value will cause all node pools to be recreated.
#   disable_legacy_metadata_endpoints: true
#   # default_max_pods_per_node - The maximum number of pods to schedule per node
#   default_max_pods_per_node: 110
#   # database_encryption - Application-layer Secrets Encryption settings. The object format is {state = string, key_name = string}. Valid values of state are: \"ENCRYPTED\"; \"DECRYPTED\". key_name is the name of a CloudKMS key.
#   database_encryption: [{"state": "DECRYPTED", "key_name": ""}]
#   # enable_shielded_nodes - Enable Shielded Nodes features on all nodes in this cluster
#   enable_shielded_nodes: true
#   # enable_binary_authorization - Enable BinAuthZ Admission controller
#   enable_binary_authorization:
#   # node_metadata - Specifies how node metadata is exposed to the workload running on the node
#   node_metadata: "GKE_METADATA"
#   # cluster_dns_provider - Which in-cluster DNS provider should be used. PROVIDER_UNSPECIFIED (default) or PLATFORM_DEFAULT or CLOUD_DNS.
#   cluster_dns_provider: "PROVIDER_UNSPECIFIED"
#   # cluster_dns_scope - The scope of access to cluster DNS records. DNS_SCOPE_UNSPECIFIED (default) or CLUSTER_SCOPE or VPC_SCOPE.
#   cluster_dns_scope: "DNS_SCOPE_UNSPECIFIED"
#   # cluster_dns_domain - The suffix used for all cluster service records.
#   cluster_dns_domain:
#   # gce_pd_csi_driver - Whether this cluster should enable the Google Compute Engine Persistent Disk Container Storage Interface (CSI) Driver.
#   gce_pd_csi_driver: true
#   # gke_backup_agent_config - Whether Backup for GKE agent is enabled for this cluster.
#   gke_backup_agent_config:
#   # timeouts - Timeout for cluster operations.
#   timeouts:
#   # monitoring_enable_managed_prometheus - Configuration for Managed Service for Prometheus. Whether or not the managed collection is enabled.
#   monitoring_enable_managed_prometheus:
#   # monitoring_enabled_components - List of services to monitor: SYSTEM_COMPONENTS, WORKLOADS (provider version >= 3.89.0). Empty list is default GKE configuration.
#   monitoring_enabled_components:
#   # logging_enabled_components - List of services to monitor: SYSTEM_COMPONENTS, WORKLOADS. Empty list is default GKE configuration.
#   logging_enabled_components:
#   # enable_kubernetes_alpha - Whether to enable Kubernetes Alpha features for this cluster. Note that when this option is enabled, the cluster cannot be upgraded and will be automatically deleted after 30 days.
#   enable_kubernetes_alpha:
#   # istio - (Beta) Enable Istio addon
#   istio:
#   # istio_auth - (Beta) The authentication type between services in Istio.
#   istio_auth: "AUTH_MUTUAL_TLS"
#   # kalm_config - (Beta) Whether KALM is enabled for this cluster.
#   kalm_config:
#   # config_connector - (Beta) Whether ConfigConnector is enabled for this cluster.
#   config_connector:
#   # cloudrun - (Beta) Enable CloudRun addon
#   cloudrun:
#   # cloudrun_load_balancer_type - (Beta) Configure the Cloud Run load balancer type. External by default. Set to `LOAD_BALANCER_TYPE_INTERNAL` to configure as an internal load balancer.
#   cloudrun_load_balancer_type:
#   # enable_pod_security_policy - enabled - Enable the PodSecurityPolicy controller for this cluster. If enabled, pods must be valid under a PodSecurityPolicy to be created.
#   enable_pod_security_policy:
#   # enable_l4_ilb_subsetting - Enable L4 ILB Subsetting on the cluster
#   enable_l4_ilb_subsetting:
#   # sandbox_enabled - (Beta) Enable GKE Sandbox (Do not forget to set `image_type` = `COS_CONTAINERD` to use it).
#   sandbox_enabled:
#   # enable_intranode_visibility - Whether Intra-node visibility is enabled for this cluster. This makes same node pod to pod traffic visible for VPC network
#   enable_intranode_visibility:
#   # enable_identity_service - Enable the Identity Service component, which allows customers to use external identity providers with the K8S API.
#   enable_identity_service:
#   # region - The region to host the cluster in (optional if zonal cluster / required if regional)
#   # region:
#   # cluster_telemetry_type - Available options include ENABLED, DISABLED, and SYSTEM_ONLY
#   # cluster_telemetry_type:
#   # cluster_ipv4_cidr - The IP address range of the kubernetes pods in this cluster. Default is an automatically assigned CIDR.
#   # cluster_ipv4_cidr:
#   # authenticator_security_group - The name of the RBAC security group for use with Google security groups in Kubernetes RBAC. Group name must be in format gke-security-groups@yourdomain.com
#   # authenticator_security_group:
#   # release_channel - The release channel of this cluster. Accepted values are `UNSPECIFIED`, `RAPID`, `REGULAR` and `STABLE`. Defaults to `UNSPECIFIED`.
#   # release_channel:
#   # gateway_api_channel - The gateway api channel of this cluster. Accepted values are `CHANNEL_STANDARD` and `CHANNEL_DISABLED`.
#   # gateway_api_channel:
# ```
#
include {
    path = find_in_parent_folders()
}

locals {
    module = {
        repository = "github.com/terraform-google-modules/terraform-google-kubernetes-engine.git"
        path = "//modules/beta-private-cluster-update-variant"
        version = "v25.0.0"
        source =  "${local.module.repository}${local.module.path != null ? local.module.path : ''}?ref=${local.module.version}"
    }
    environment = get_env("ENV", "development")
    all = merge(
        yamldecode(file(find_in_parent_folders(format("config.%s.yaml", local.environment)))),
    )
}

terraform {
    source = lookup(local.all["beta-private-cluster-update-variant"], "enabled", true) == true ? local.module.source : null
}

inputs = merge({
    # ip_range_pods - The _name_ of the secondary subnet ip range to use for pods - required
    ip_range_pods = lookup(local.all["beta-private-cluster-update-variant"], "ip_range_pods", "")
    # ip_range_services - The _name_ of the secondary subnet range to use for services - required
    ip_range_services = lookup(local.all["beta-private-cluster-update-variant"], "ip_range_services", "")
    # name - The name of the cluster (required) - required
    name = lookup(local.all["beta-private-cluster-update-variant"], "name", "")
    # network - The VPC network to host the cluster in (required) - required
    network = lookup(local.all["beta-private-cluster-update-variant"], "network", "")
    # project_id - The project ID to host the cluster in (required) - required
    project_id = lookup(local.all["beta-private-cluster-update-variant"], "project_id", "")
    # subnetwork - The subnetwork to host the cluster in (required) - required
    subnetwork = lookup(local.all["beta-private-cluster-update-variant"], "subnetwork", "")
    # add_cluster_firewall_rules - Create additional firewall rules
    add_cluster_firewall_rules = lookup(local.all["beta-private-cluster-update-variant"], "add_cluster_firewall_rules", false)
    # add_master_webhook_firewall_rules - Create master_webhook firewall rules for ports defined in `firewall_inbound_ports`
    add_master_webhook_firewall_rules = lookup(local.all["beta-private-cluster-update-variant"], "add_master_webhook_firewall_rules", false)
    # add_shadow_firewall_rules - Create GKE shadow firewall (the same as default firewall rules with firewall logs enabled).
    add_shadow_firewall_rules = lookup(local.all["beta-private-cluster-update-variant"], "add_shadow_firewall_rules", false)
    # cloudrun - (Beta) Enable CloudRun addon
    cloudrun = lookup(local.all["beta-private-cluster-update-variant"], "cloudrun", false)
    # cloudrun_load_balancer_type - (Beta) Configure the Cloud Run load balancer type. External by default. Set to `LOAD_BALANCER_TYPE_INTERNAL` to configure as an internal load balancer.
    cloudrun_load_balancer_type = lookup(local.all["beta-private-cluster-update-variant"], "cloudrun_load_balancer_type", "")
    # cluster_autoscaling - Cluster autoscaling configuration. See [more details](https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1beta1/projects.locations.clusters#clusterautoscaling)
    cluster_autoscaling = lookup(local.all["beta-private-cluster-update-variant"], "cluster_autoscaling", {"enabled": false, "autoscaling_profile": "BALANCED", "max_cpu_cores": 0, "min_cpu_cores": 0, "max_memory_gb": 0, "min_memory_gb": 0, "gpu_resources": [], "auto_repair": true, "auto_upgrade": true})
    # cluster_dns_domain - The suffix used for all cluster service records.
    cluster_dns_domain = lookup(local.all["beta-private-cluster-update-variant"], "cluster_dns_domain", "")
    # cluster_dns_provider - Which in-cluster DNS provider should be used. PROVIDER_UNSPECIFIED (default) or PLATFORM_DEFAULT or CLOUD_DNS.
    cluster_dns_provider = lookup(local.all["beta-private-cluster-update-variant"], "cluster_dns_provider", "PROVIDER_UNSPECIFIED")
    # cluster_dns_scope - The scope of access to cluster DNS records. DNS_SCOPE_UNSPECIFIED (default) or CLUSTER_SCOPE or VPC_SCOPE.
    cluster_dns_scope = lookup(local.all["beta-private-cluster-update-variant"], "cluster_dns_scope", "DNS_SCOPE_UNSPECIFIED")
    # cluster_resource_labels - The GCE resource labels (a map of key/value pairs) to be applied to the cluster
    cluster_resource_labels = lookup(local.all["beta-private-cluster-update-variant"], "cluster_resource_labels", {})
    # config_connector - (Beta) Whether ConfigConnector is enabled for this cluster.
    config_connector = lookup(local.all["beta-private-cluster-update-variant"], "config_connector", false)
    # configure_ip_masq - Enables the installation of ip masquerading, which is usually no longer required when using aliasied IP addresses. IP masquerading uses a kubectl call, so when you have a private cluster, you will need access to the API server.
    configure_ip_masq = lookup(local.all["beta-private-cluster-update-variant"], "configure_ip_masq", false)
    # create_service_account - Defines if service account specified to run nodes should be created.
    create_service_account = lookup(local.all["beta-private-cluster-update-variant"], "create_service_account", true)
    # database_encryption - Application-layer Secrets Encryption settings. The object format is {state = string, key_name = string}. Valid values of state are: "ENCRYPTED"; "DECRYPTED". key_name is the name of a CloudKMS key.
    database_encryption = lookup(local.all["beta-private-cluster-update-variant"], "database_encryption", [{"state": "DECRYPTED", "key_name": ""}])
    # datapath_provider - The desired datapath provider for this cluster. By default, `DATAPATH_PROVIDER_UNSPECIFIED` enables the IPTables-based kube-proxy implementation. `ADVANCED_DATAPATH` enables Dataplane-V2 feature.
    datapath_provider = lookup(local.all["beta-private-cluster-update-variant"], "datapath_provider", "DATAPATH_PROVIDER_UNSPECIFIED")
    # default_max_pods_per_node - The maximum number of pods to schedule per node
    default_max_pods_per_node = lookup(local.all["beta-private-cluster-update-variant"], "default_max_pods_per_node", 110)
    # deploy_using_private_endpoint - (Beta) A toggle for Terraform and kubectl to connect to the master's internal IP address during deployment.
    deploy_using_private_endpoint = lookup(local.all["beta-private-cluster-update-variant"], "deploy_using_private_endpoint", false)
    # description - The description of the cluster
    description = lookup(local.all["beta-private-cluster-update-variant"], "description", "")
    # disable_default_snat - Whether to disable the default SNAT to support the private use of public IP addresses
    disable_default_snat = lookup(local.all["beta-private-cluster-update-variant"], "disable_default_snat", false)
    # disable_legacy_metadata_endpoints - Disable the /0.1/ and /v1beta1/ metadata server endpoints on the node. Changing this value will cause all node pools to be recreated.
    disable_legacy_metadata_endpoints = lookup(local.all["beta-private-cluster-update-variant"], "disable_legacy_metadata_endpoints", true)
    # dns_cache - The status of the NodeLocal DNSCache addon.
    dns_cache = lookup(local.all["beta-private-cluster-update-variant"], "dns_cache", false)
    # enable_binary_authorization - Enable BinAuthZ Admission controller
    enable_binary_authorization = lookup(local.all["beta-private-cluster-update-variant"], "enable_binary_authorization", false)
    # enable_confidential_nodes - An optional flag to enable confidential node config.
    enable_confidential_nodes = lookup(local.all["beta-private-cluster-update-variant"], "enable_confidential_nodes", false)
    # enable_cost_allocation - Enables Cost Allocation Feature and the cluster name and namespace of your GKE workloads appear in the labels field of the billing export to BigQuery
    enable_cost_allocation = lookup(local.all["beta-private-cluster-update-variant"], "enable_cost_allocation", false)
    # enable_identity_service - Enable the Identity Service component, which allows customers to use external identity providers with the K8S API.
    enable_identity_service = lookup(local.all["beta-private-cluster-update-variant"], "enable_identity_service", false)
    # enable_intranode_visibility - Whether Intra-node visibility is enabled for this cluster. This makes same node pod to pod traffic visible for VPC network
    enable_intranode_visibility = lookup(local.all["beta-private-cluster-update-variant"], "enable_intranode_visibility", false)
    # enable_kubernetes_alpha - Whether to enable Kubernetes Alpha features for this cluster. Note that when this option is enabled, the cluster cannot be upgraded and will be automatically deleted after 30 days.
    enable_kubernetes_alpha = lookup(local.all["beta-private-cluster-update-variant"], "enable_kubernetes_alpha", false)
    # enable_l4_ilb_subsetting - Enable L4 ILB Subsetting on the cluster
    enable_l4_ilb_subsetting = lookup(local.all["beta-private-cluster-update-variant"], "enable_l4_ilb_subsetting", false)
    # enable_network_egress_export - Whether to enable network egress metering for this cluster. If enabled, a daemonset will be created in the cluster to meter network egress traffic.
    enable_network_egress_export = lookup(local.all["beta-private-cluster-update-variant"], "enable_network_egress_export", false)
    # enable_pod_security_policy - enabled - Enable the PodSecurityPolicy controller for this cluster. If enabled, pods must be valid under a PodSecurityPolicy to be created.
    enable_pod_security_policy = lookup(local.all["beta-private-cluster-update-variant"], "enable_pod_security_policy", false)
    # enable_private_endpoint - (Beta) Whether the master's internal IP address is used as the cluster endpoint
    enable_private_endpoint = lookup(local.all["beta-private-cluster-update-variant"], "enable_private_endpoint", false)
    # enable_private_nodes - (Beta) Whether nodes have internal IP addresses only
    enable_private_nodes = lookup(local.all["beta-private-cluster-update-variant"], "enable_private_nodes", false)
    # enable_resource_consumption_export - Whether to enable resource consumption metering on this cluster. When enabled, a table will be created in the resource export BigQuery dataset to store resource consumption data. The resulting table can be joined with the resource usage table or with BigQuery billing export.
    enable_resource_consumption_export = lookup(local.all["beta-private-cluster-update-variant"], "enable_resource_consumption_export", true)
    # enable_shielded_nodes - Enable Shielded Nodes features on all nodes in this cluster
    enable_shielded_nodes = lookup(local.all["beta-private-cluster-update-variant"], "enable_shielded_nodes", true)
    # enable_tpu - Enable Cloud TPU resources in the cluster. WARNING: changing this after cluster creation is destructive!
    enable_tpu = lookup(local.all["beta-private-cluster-update-variant"], "enable_tpu", false)
    # enable_vertical_pod_autoscaling - Vertical Pod Autoscaling automatically adjusts the resources of pods controlled by it
    enable_vertical_pod_autoscaling = lookup(local.all["beta-private-cluster-update-variant"], "enable_vertical_pod_autoscaling", false)
    # filestore_csi_driver - The status of the Filestore CSI driver addon, which allows the usage of filestore instance as volumes
    filestore_csi_driver = lookup(local.all["beta-private-cluster-update-variant"], "filestore_csi_driver", false)
    # firewall_inbound_ports - List of TCP ports for admission/webhook controllers. Either flag `add_master_webhook_firewall_rules` or `add_cluster_firewall_rules` (also adds egress rules) must be set to `true` for inbound-ports firewall rules to be applied.
    firewall_inbound_ports = lookup(local.all["beta-private-cluster-update-variant"], "firewall_inbound_ports", ["8443", "9443", "15017"])
    # firewall_priority - Priority rule for firewall rules
    firewall_priority = lookup(local.all["beta-private-cluster-update-variant"], "firewall_priority", 1000)
    # gce_pd_csi_driver - Whether this cluster should enable the Google Compute Engine Persistent Disk Container Storage Interface (CSI) Driver.
    gce_pd_csi_driver = lookup(local.all["beta-private-cluster-update-variant"], "gce_pd_csi_driver", true)
    # gke_backup_agent_config - Whether Backup for GKE agent is enabled for this cluster.
    gke_backup_agent_config = lookup(local.all["beta-private-cluster-update-variant"], "gke_backup_agent_config", false)
    # grant_registry_access - Grants created cluster-specific service account storage.objectViewer and artifactregistry.reader roles.
    grant_registry_access = lookup(local.all["beta-private-cluster-update-variant"], "grant_registry_access", false)
    # horizontal_pod_autoscaling - Enable horizontal pod autoscaling addon
    horizontal_pod_autoscaling = lookup(local.all["beta-private-cluster-update-variant"], "horizontal_pod_autoscaling", true)
    # http_load_balancing - Enable httpload balancer addon
    http_load_balancing = lookup(local.all["beta-private-cluster-update-variant"], "http_load_balancing", true)
    # identity_namespace - The workload pool to attach all Kubernetes service accounts to. (Default value of `enabled` automatically sets project-based pool `[project_id].svc.id.goog`)
    identity_namespace = lookup(local.all["beta-private-cluster-update-variant"], "identity_namespace", "enabled")
    # initial_node_count - The number of nodes to create in this cluster's default node pool.
    initial_node_count = lookup(local.all["beta-private-cluster-update-variant"], "initial_node_count", 0)
    # ip_masq_link_local - Whether to masquerade traffic to the link-local prefix (169.254.0.0/16).
    ip_masq_link_local = lookup(local.all["beta-private-cluster-update-variant"], "ip_masq_link_local", false)
    # ip_masq_resync_interval - The interval at which the agent attempts to sync its ConfigMap file from the disk.
    ip_masq_resync_interval = lookup(local.all["beta-private-cluster-update-variant"], "ip_masq_resync_interval", "60s")
    # issue_client_certificate - Issues a client certificate to authenticate to the cluster endpoint. To maximize the security of your cluster, leave this option disabled. Client certificates don't automatically rotate and aren't easily revocable. WARNING: changing this after cluster creation is destructive!
    issue_client_certificate = lookup(local.all["beta-private-cluster-update-variant"], "issue_client_certificate", false)
    # istio - (Beta) Enable Istio addon
    istio = lookup(local.all["beta-private-cluster-update-variant"], "istio", false)
    # istio_auth - (Beta) The authentication type between services in Istio.
    istio_auth = lookup(local.all["beta-private-cluster-update-variant"], "istio_auth", "AUTH_MUTUAL_TLS")
    # kalm_config - (Beta) Whether KALM is enabled for this cluster.
    kalm_config = lookup(local.all["beta-private-cluster-update-variant"], "kalm_config", false)
    # kubernetes_version - The Kubernetes version of the masters. If set to 'latest' it will pull latest available version in the selected region.
    kubernetes_version = lookup(local.all["beta-private-cluster-update-variant"], "kubernetes_version", "latest")
    # logging_enabled_components - List of services to monitor: SYSTEM_COMPONENTS, WORKLOADS. Empty list is default GKE configuration.
    logging_enabled_components = lookup(local.all["beta-private-cluster-update-variant"], "logging_enabled_components", [])
    # logging_service - The logging service that the cluster should write logs to. Available options include logging.googleapis.com, logging.googleapis.com/kubernetes (beta), and none
    logging_service = lookup(local.all["beta-private-cluster-update-variant"], "logging_service", "logging.googleapis.com/kubernetes")
    # maintenance_end_time - Time window specified for recurring maintenance operations in RFC3339 format
    maintenance_end_time = lookup(local.all["beta-private-cluster-update-variant"], "maintenance_end_time", "")
    # maintenance_exclusions - List of maintenance exclusions. A cluster can have up to three
    maintenance_exclusions = lookup(local.all["beta-private-cluster-update-variant"], "maintenance_exclusions", [])
    # maintenance_recurrence - Frequency of the recurring maintenance window in RFC5545 format.
    maintenance_recurrence = lookup(local.all["beta-private-cluster-update-variant"], "maintenance_recurrence", "")
    # maintenance_start_time - Time window specified for daily or recurring maintenance operations in RFC3339 format
    maintenance_start_time = lookup(local.all["beta-private-cluster-update-variant"], "maintenance_start_time", "05:00")
    # master_authorized_networks - List of master authorized networks. If none are provided, disallow external access (except the cluster node IPs, which GKE automatically whitelists).
    master_authorized_networks = lookup(local.all["beta-private-cluster-update-variant"], "master_authorized_networks", [])
    # master_global_access_enabled - Whether the cluster master is accessible globally (from any region) or only within the same region as the private endpoint.
    master_global_access_enabled = lookup(local.all["beta-private-cluster-update-variant"], "master_global_access_enabled", true)
    # master_ipv4_cidr_block - (Beta) The IP range in CIDR notation to use for the hosted master network
    master_ipv4_cidr_block = lookup(local.all["beta-private-cluster-update-variant"], "master_ipv4_cidr_block", "10.0.0.0/28")
    # monitoring_enable_managed_prometheus - Configuration for Managed Service for Prometheus. Whether or not the managed collection is enabled.
    monitoring_enable_managed_prometheus = lookup(local.all["beta-private-cluster-update-variant"], "monitoring_enable_managed_prometheus", false)
    # monitoring_enabled_components - List of services to monitor: SYSTEM_COMPONENTS, WORKLOADS (provider version >= 3.89.0). Empty list is default GKE configuration.
    monitoring_enabled_components = lookup(local.all["beta-private-cluster-update-variant"], "monitoring_enabled_components", [])
    # monitoring_service - The monitoring service that the cluster should write metrics to. Automatically send metrics from pods in the cluster to the Google Cloud Monitoring API. VM metrics will be collected by Google Compute Engine regardless of this setting Available options include monitoring.googleapis.com, monitoring.googleapis.com/kubernetes (beta) and none
    monitoring_service = lookup(local.all["beta-private-cluster-update-variant"], "monitoring_service", "monitoring.googleapis.com/kubernetes")
    # network_policy - Enable network policy addon
    network_policy = lookup(local.all["beta-private-cluster-update-variant"], "network_policy", false)
    # network_policy_provider - The network policy provider.
    network_policy_provider = lookup(local.all["beta-private-cluster-update-variant"], "network_policy_provider", "CALICO")
    # network_project_id - The project ID of the shared VPC's host (for shared vpc support)
    network_project_id = lookup(local.all["beta-private-cluster-update-variant"], "network_project_id", "")
    # node_metadata - Specifies how node metadata is exposed to the workload running on the node
    node_metadata = lookup(local.all["beta-private-cluster-update-variant"], "node_metadata", "GKE_METADATA")
    # node_pools - List of maps containing node pools
    node_pools = lookup(local.all["beta-private-cluster-update-variant"], "node_pools", [{"name": "default-node-pool"}])
    # node_pools_labels - Map of maps containing node labels by node-pool name
    node_pools_labels = lookup(local.all["beta-private-cluster-update-variant"], "node_pools_labels", {"all": {}, "default-node-pool": {}})
    # node_pools_linux_node_configs_sysctls - Map of maps containing linux node config sysctls by node-pool name
    node_pools_linux_node_configs_sysctls = lookup(local.all["beta-private-cluster-update-variant"], "node_pools_linux_node_configs_sysctls", {"all": {}, "default-node-pool": {}})
    # node_pools_metadata - Map of maps containing node metadata by node-pool name
    node_pools_metadata = lookup(local.all["beta-private-cluster-update-variant"], "node_pools_metadata", {"all": {}, "default-node-pool": {}})
    # node_pools_oauth_scopes - Map of lists containing node oauth scopes by node-pool name
    node_pools_oauth_scopes = lookup(local.all["beta-private-cluster-update-variant"], "node_pools_oauth_scopes", {"all": ["https://www.googleapis.com/auth/cloud-platform"], "default-node-pool": []})
    # node_pools_resource_labels - Map of maps containing resource labels by node-pool name
    node_pools_resource_labels = lookup(local.all["beta-private-cluster-update-variant"], "node_pools_resource_labels", {"all": {}, "default-node-pool": {}})
    # node_pools_tags - Map of lists containing node network tags by node-pool name
    node_pools_tags = lookup(local.all["beta-private-cluster-update-variant"], "node_pools_tags", {"all": [], "default-node-pool": []})
    # node_pools_taints - Map of lists containing node taints by node-pool name
    node_pools_taints = lookup(local.all["beta-private-cluster-update-variant"], "node_pools_taints", {"all": [], "default-node-pool": []})
    # non_masquerade_cidrs - List of strings in CIDR notation that specify the IP address ranges that do not use IP masquerading.
    non_masquerade_cidrs = lookup(local.all["beta-private-cluster-update-variant"], "non_masquerade_cidrs", ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"])
    # notification_config_topic - The desired Pub/Sub topic to which notifications will be sent by GKE. Format is projects/{project}/topics/{topic}.
    notification_config_topic = lookup(local.all["beta-private-cluster-update-variant"], "notification_config_topic", "")
    # regional - Whether is a regional cluster (zonal cluster if set false. WARNING: changing this after cluster creation is destructive!)
    regional = lookup(local.all["beta-private-cluster-update-variant"], "regional", true)
    # registry_project_ids - Projects holding Google Container Registries. If empty, we use the cluster project. If a service account is created and the `grant_registry_access` variable is set to `true`, the `storage.objectViewer` and `artifactregsitry.reader` roles are assigned on these projects.
    registry_project_ids = lookup(local.all["beta-private-cluster-update-variant"], "registry_project_ids", [])
    # remove_default_node_pool - Remove default node pool while setting up the cluster
    remove_default_node_pool = lookup(local.all["beta-private-cluster-update-variant"], "remove_default_node_pool", false)
    # resource_usage_export_dataset_id - The ID of a BigQuery Dataset for using BigQuery as the destination of resource usage export.
    resource_usage_export_dataset_id = lookup(local.all["beta-private-cluster-update-variant"], "resource_usage_export_dataset_id", "")
    # sandbox_enabled - (Beta) Enable GKE Sandbox (Do not forget to set `image_type` = `COS_CONTAINERD` to use it).
    sandbox_enabled = lookup(local.all["beta-private-cluster-update-variant"], "sandbox_enabled", false)
    # service_account - The service account to run nodes as if not overridden in `node_pools`. The create_service_account variable default value (true) will cause a cluster-specific service account to be created.
    service_account = lookup(local.all["beta-private-cluster-update-variant"], "service_account", "")
    # service_external_ips - Whether external ips specified by a service will be allowed in this cluster
    service_external_ips = lookup(local.all["beta-private-cluster-update-variant"], "service_external_ips", false)
    # shadow_firewall_rules_log_config - The log_config for shadow firewall rules. You can set this variable to `null` to disable logging.
    shadow_firewall_rules_log_config = lookup(local.all["beta-private-cluster-update-variant"], "shadow_firewall_rules_log_config", {"metadata": "INCLUDE_ALL_METADATA"})
    # shadow_firewall_rules_priority - The firewall priority of GKE shadow firewall rules. The priority should be less than default firewall, which is 1000.
    shadow_firewall_rules_priority = lookup(local.all["beta-private-cluster-update-variant"], "shadow_firewall_rules_priority", 999)
    # skip_provisioners - Flag to skip all local-exec provisioners. It breaks `stub_domains` and `upstream_nameservers` variables functionality.
    skip_provisioners = lookup(local.all["beta-private-cluster-update-variant"], "skip_provisioners", false)
    # stub_domains - Map of stub domains and their resolvers to forward DNS queries for a certain domain to an external DNS server
    stub_domains = lookup(local.all["beta-private-cluster-update-variant"], "stub_domains", {})
    # timeouts - Timeout for cluster operations.
    timeouts = lookup(local.all["beta-private-cluster-update-variant"], "timeouts", {})
    # upstream_nameservers - If specified, the values replace the nameservers taken by default from the node’s /etc/resolv.conf
    upstream_nameservers = lookup(local.all["beta-private-cluster-update-variant"], "upstream_nameservers", [])
    # windows_node_pools - List of maps containing Windows node pools
    windows_node_pools = lookup(local.all["beta-private-cluster-update-variant"], "windows_node_pools", [])
    # zones - The zones to host the cluster in (optional if regional cluster / required if zonal)
    zones = lookup(local.all["beta-private-cluster-update-variant"], "zones", [])
},
  # authenticator_security_group - The name of the RBAC security group for use with Google security groups in Kubernetes RBAC. Group name must be in format gke-security-groups@yourdomain.com
  (lookup(local.all["beta-private-cluster-update-variant"], "authenticator_security_group", null) == null ? {} : { authenticator_security_group =  lookup(local.all["beta-private-cluster-update-variant"], "authenticator_security_group") }),
  # cluster_ipv4_cidr - The IP address range of the kubernetes pods in this cluster. Default is an automatically assigned CIDR.
  (lookup(local.all["beta-private-cluster-update-variant"], "cluster_ipv4_cidr", null) == null ? {} : { cluster_ipv4_cidr =  lookup(local.all["beta-private-cluster-update-variant"], "cluster_ipv4_cidr") }),
  # cluster_telemetry_type - Available options include ENABLED, DISABLED, and SYSTEM_ONLY
  (lookup(local.all["beta-private-cluster-update-variant"], "cluster_telemetry_type", null) == null ? {} : { cluster_telemetry_type =  lookup(local.all["beta-private-cluster-update-variant"], "cluster_telemetry_type") }),
  # gateway_api_channel - The gateway api channel of this cluster. Accepted values are `CHANNEL_STANDARD` and `CHANNEL_DISABLED`.
  (lookup(local.all["beta-private-cluster-update-variant"], "gateway_api_channel", null) == null ? {} : { gateway_api_channel =  lookup(local.all["beta-private-cluster-update-variant"], "gateway_api_channel") }),
  # region - The region to host the cluster in (optional if zonal cluster / required if regional)
  (lookup(local.all["beta-private-cluster-update-variant"], "region", null) == null ? {} : { region =  lookup(local.all["beta-private-cluster-update-variant"], "region") }),
  # release_channel - The release channel of this cluster. Accepted values are `UNSPECIFIED`, `RAPID`, `REGULAR` and `STABLE`. Defaults to `UNSPECIFIED`.
  (lookup(local.all["beta-private-cluster-update-variant"], "release_channel", null) == null ? {} : { release_channel =  lookup(local.all["beta-private-cluster-update-variant"], "release_channel") })
)

```
