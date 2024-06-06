/*
  All variables are stored here
*/

# dev, stage, prod, qa, lab, sales, demo, support
variable "workload_classification" {
  default     = "dev"
  description = "Infosec required tag for compliance tools"
  validation {
    condition = anytrue([
      var.workload_classification == "dev",
      var.workload_classification == "stage",
      var.workload_classification == "prod",
      var.workload_classification == "qa",
      var.workload_classification == "sales",
      var.workload_classification == "demo",
      var.workload_classification == "support"
    ])
    error_message = "Workload Classification must match one of the valid labels."
  }
}

variable "environment" { default = "dev" }
variable "region" { default = "eu-west-1" }
variable "customer_cidrs" { default = "0.0.0.0/0" }
variable "customer_cidrs_ipv6" { default = "::/0" }
variable "compute_size" { default = 5 }
variable "live_storage" { default = 1 }
variable "archive_storage" { default = 0 }
variable "serial_number" { default = "siemtest" }
variable "hosted_zone_id" {
  type = map(string)
  default = {
    "dev"        = "Z059492637I0IWV7W2CUD"
    "playground" = "Z0068319122PMERT3SQEU"
    "prod"       = "Z06385452ZZ6AXQGN4WN0"
  }
}

variable "hosted_zone_name" {
  type = map(string)
  default = {
    "dev"        = "dev.fortisiem.cloud"
    "playground" = "playground.fortisiem.cloud"
    "prod"       = "fortisiem.cloud"
  }
}

variable "default_password" { default = "admin*1" }
variable "deployment_email" { default = "test@var.com" }
variable "deployment_type" { default = "va" }
variable "is_poc" {
  type    = bool
  default = false
}

# Defaults to smallest ClickHouse deployment
variable "shards" { default = 0 }
variable "replicas" { default = 0 }
variable "data_workers" { default = 2 }
variable "ingestion_workers" { default = 0 }
variable "keeper_workers" { default = 0 }
variable "super_instance_types" {
  type    = list(string)
  default = ["m6i.2xlarge", "m6a.2xlarge", "m5.2xlarge"]
}
variable "worker_instance_types" {
  type    = list(string)
  default = ["m6i.xlarge", "m6a.xlarge", "m5.xlarge"]
}
variable "keeper_instance_types" {
  type    = list(string)
  default = ["c6i.xlarge", "c6a.xlarge", "c5.xlarge"]
}
variable "ingestion_instance_types" {
  type    = list(string)
  default = ["c6i.xlarge", "c6a.xlarge", "c5.xlarge"]
}
variable "cmdb_iops" { default = 3000 }
variable "cmdb_throughput" { default = 125 }
variable "opt_iops" { default = 3000 }      # AWS default for gp3, disk size 100 GB
variable "opt_throughput" { default = 125 } # AWS default for gp3, disk size 100 GB
variable "data_disk_throughput" { default = 125 }
variable "data_disk_iops" { default = 3000 }
variable "data_disk_count" { default = 5 }
variable "data_disk_size" { default = 110 }
variable "app_server_mem_gb" { default = 5 }

# S3
# This S3 bucket contains scripts for VM configuration
variable "vm_bucket" { default = "fsiem-terraform" }

variable "alternate_domain_certificate_arn" { default = "" }

# Primary Availability Zone for this specific deployment
# this comes in when the deployment is provisioned
variable "primary_az" { default = "" }

# External storage destinations
variable "external_storage_dests" {
  type = map(string)
  default = {
    "ALL" = "fsiem-extn-storage-bkt"
  }
}

variable "external_storage_prefix" { default = "fsiemextstr" }

# Network firewall optional flag
variable "has_nfw" {
  type    = bool
  default = false
}

variable "log_persistance_days_long" {
  type = map(string)
  default = {
    "dev"        = 30
    "playground" = 30
    "prod"       = 365
  }
}
variable "log_persistance_days_medium" {
  type = map(string)
  default = {
    "dev"        = 14
    "playground" = 14
    "prod"       = 30
  }
}
variable "log_persistance_days_short" {
  type = map(string)
  default = {
    "dev"        = 7
    "playground" = 7
    "prod"       = 14
  }
}

locals {
  # AWS account id (023941436530 - dev/playgrpound, 327332988639 - prod)
  account_id = data.aws_caller_identity.current.account_id

  # The region where main portal and infrustructure is deployed
  portal_region = "us-east-1"

  global_tags = {
    Terraform              = "true"
    Environment            = var.environment
    WorkloadClassification = var.workload_classification
    ProductName            = "FortiSIEM Cloud"
    SerialNumber           = var.serial_number
    POC                    = var.is_poc
    NumberOfSeats          = var.compute_size
  }
  fortimonitor_arn = {
    "dev"        = "arn:aws:secretsmanager:${var.region}:${local.account_id}:secret:fortimonitor-${var.environment}-pIZx9k"
    "playground" = "arn:aws:secretsmanager:${var.region}:${local.account_id}:secret:fortimonitor-${var.environment}-epghX1"
    "prod"       = "arn:aws:secretsmanager:${var.region}:${local.account_id}:secret:fortimonitor-${var.environment}-6AutUA"
  }
  cognito_url = "https://forticloud-fsiem-${var.environment}.auth.${local.portal_region}.amazoncognito.com"
  portal_api_url = {
    "dev"        = "https://zh71vh4fxj.execute-api.${local.portal_region}.amazonaws.com/${var.environment}-stage"
    "playground" = "https://oo35plz18d.execute-api.${local.portal_region}.amazonaws.com/${var.environment}-stage"
    "prod"       = "https://dgj5jqjayc.execute-api.${local.portal_region}.amazonaws.com/${var.environment}-stage"
  }
  fsiem_ecr_base_repo_url               = "${local.account_id}.dkr.ecr.${var.region}.amazonaws.com"
  fsiem_ecr_base_tag                    = "latest"
  fsiem_backup_ecr_repo_url             = "${local.fsiem_ecr_base_repo_url}/fsiem-backup-${var.environment}:${local.fsiem_ecr_base_tag}"
  fsiem_setup_ecr_repo_url              = "${local.fsiem_ecr_base_repo_url}/fsiem-setup-${var.environment}:${local.fsiem_ecr_base_tag}"
  fsiem_storage_enforcer_ecr_repo_url   = "${local.fsiem_ecr_base_repo_url}/fsiem-storage-enforcer-${var.environment}:${local.fsiem_ecr_base_tag}"
  fsiem_license_ecr_repo_url            = "${local.fsiem_ecr_base_repo_url}/fsiem-license-${var.environment}:${local.fsiem_ecr_base_tag}"
  fsiem_metrics_ecr_repo_url            = "${local.fsiem_ecr_base_repo_url}/fsiem-metrics-${var.environment}:${local.fsiem_ecr_base_tag}"
  fsiem_monitor_ecr_repo_url            = "${local.fsiem_ecr_base_repo_url}/fsiem-monitor-${var.environment}:${local.fsiem_ecr_base_tag}"
  fsiem_worker_autoscaling_ecr_repo_url = "${local.fsiem_ecr_base_repo_url}/fsiem-worker-lifecycle-${var.environment}:${local.fsiem_ecr_base_tag}"
  parameter_admin_password_arn          = "arn:aws:ssm:${local.portal_region}:${local.account_id}:parameter/${var.serial_number}/admin_password"
  ingress_cidrs_ipv4                    = compact(split(",", var.customer_cidrs))
  ingress_cidrs_ipv6                    = compact(split(",", var.customer_cidrs_ipv6))
  waf_super                             = "waf_super_${var.environment}"
  session_manager_bucket_arn            = "arn:aws:s3:::fsiem-session-manager-logs-${var.environment}"
  live_size_limit_gb                    = var.live_storage * 500
  archive_size_limit_gb                 = var.archive_storage * 500

  # e.g. fsiem-terraform-dev-scripts
  s3_scripts_bucket              = "${var.vm_bucket}-${var.environment}-scripts"
  s3_taclogs_bucket              = "${var.vm_bucket}-${var.environment}-taclogs"
  s3_scripts_bucket_arn          = "arn:aws:s3:::${local.s3_scripts_bucket}"
  s3_taclogs_bucket_arn          = "arn:aws:s3:::${local.s3_taclogs_bucket}"
  s3_upgrade_packages_bucket_arn = "arn:aws:s3:::fsiem-${var.environment}-upgrade-packages"


  # EBS disk timeout values defaults
  # used for all EBS actions, defaults are normally
  # 5 minutes which in most cases is too short
  create_timeout = "15m"
  update_timeout = "15m"
  delete_timeout = "30m"

  # this is a standard format for all clickhouse data buckets
  # there will be one per region
  clickhouse_data_bucket      = "fsiem-clickhouse-data-${var.region}-${var.environment}"
  clickhouse_data_arn         = "arn:aws:s3:::${local.clickhouse_data_bucket}"
  clickhouse_archive_dir_name = var.serial_number

  # Clickhouse S3 backups
  clickhouse_backup_bucket   = "fsiem-clickhouse-backups-${var.region}-${var.environment}"
  clickhouse_backup_arn      = "arn:aws:s3:::${local.clickhouse_backup_bucket}"
  clickhouse_backup_dir_name = var.serial_number

  # Web certificate for MSSP's alternate domain
  has_alternate_certificiate = var.alternate_domain_certificate_arn != ""

  # Keeper disk size in GB
  keeper_disk_size = 200

  # if we are using CH then we choose 1 primary az (this comes in via Provisioning API)
  # else choose the first one from the list of availability zones in that aws region
  primary_availability_zone = var.primary_az == "" ? [data.aws_availability_zones.available.names[0]] : [var.primary_az]

  # Network firewall rules arns mappings
  # Stateless rulegroup arns
  nfw_sl_rules_arn = {
    "icmp" = "arn:aws:network-firewall:${var.region}:${local.account_id}:stateless-rulegroup/icmp-${var.environment}"
  }
  # Statefull rulegroup arns
  nfw_sf_rules_arn_prefix = "arn:aws:network-firewall:${var.region}:${local.account_id}:stateful-rulegroup"
  nfw_sf_rules_arn = {
    "dns"   = "${local.nfw_sf_rules_arn_prefix}/dns-${var.environment}"
    "ntp"   = "${local.nfw_sf_rules_arn_prefix}/ntp-${var.environment}"
    "smb"   = "${local.nfw_sf_rules_arn_prefix}/smb-${var.environment}"
    "smtp"  = "${local.nfw_sf_rules_arn_prefix}/smtp-${var.environment}"
    "http"  = "${local.nfw_sf_rules_arn_prefix}/http-${var.environment}"
    "snmp"  = "${local.nfw_sf_rules_arn_prefix}/snmp-${var.environment}"
    "slog"  = "${local.nfw_sf_rules_arn_prefix}/syslog-${var.environment}"
    "tftp"  = "${local.nfw_sf_rules_arn_prefix}/tftp-${var.environment}"
    "rpc"   = "${local.nfw_sf_rules_arn_prefix}/rpc-${var.environment}"
    "nbtcp" = "${local.nfw_sf_rules_arn_prefix}/netbios-tcp-${var.environment}"
    "nbudp" = "${local.nfw_sf_rules_arn_prefix}/netbios-udp-${var.environment}"
    "irc"   = "${local.nfw_sf_rules_arn_prefix}/irc-${var.environment}"
    "ftp"   = "${local.nfw_sf_rules_arn_prefix}/ftp-${var.environment}"
    "imap"  = "${local.nfw_sf_rules_arn_prefix}/imap-${var.environment}"
    "ssh"   = "${local.nfw_sf_rules_arn_prefix}/ssh-${var.environment}"
    "dhcp"  = "${local.nfw_sf_rules_arn_prefix}/dhcp-${var.environment}"
  }

  # DynamoDb tables
  dynamodb_activation_table             = "fsiem_activation_table_${var.environment}"
  dynamodb_activation_table_arn         = "arn:aws:dynamodb:${local.portal_region}:${local.account_id}:table/${local.dynamodb_activation_table}"
  dynamodb_metrics_storage_table        = "fsiem_metrics_storage_${var.environment}"
  dynamodb_metrics_storage_table_arn    = "arn:aws:dynamodb:${local.portal_region}:${local.account_id}:table/${local.dynamodb_metrics_storage_table}"
  dynamodb_backup_table                 = "fsiem_clickhouse_backup_${var.environment}"
  dynamodb_backup_table_arn             = "arn:aws:dynamodb:${local.portal_region}:${local.account_id}:table/${local.dynamodb_backup_table}"
  dynamodb_backup_options_table         = "fsiem_backup_options_${var.environment}"
  dynamodb_backup_options_table_arn     = "arn:aws:dynamodb:${local.portal_region}:${local.account_id}:table/${local.dynamodb_backup_options_table}"
  dynamodb_restore_table                = "fsiem_clickhouse_restore_${var.environment}"
  dynamodb_restore_table_arn            = "arn:aws:dynamodb:${local.portal_region}:${local.account_id}:table/${local.dynamodb_restore_table}"
  dynamodb_ext_storage_table            = "fsiem_external_storage_table_${var.environment}"
  dynamodb_ext_storage_table_arn        = "arn:aws:dynamodb:${local.portal_region}:${local.account_id}:table/${local.dynamodb_ext_storage_table}"
  dynamodb_ext_storage_status_table     = "fsiem_external_storage_status_table_${var.environment}"
  dynamodb_ext_storage_status_table_arn = "arn:aws:dynamodb:${local.portal_region}:${local.account_id}:table/${local.dynamodb_ext_storage_status_table}"

  # Email addresses for FortiSIEM cloud team, use this for TO and FROM email addresses
  email_from_addr = "no-reply@mail.${var.environment}.fortisiem.cloud"
  email_to_addr   = "fortisiem-cloud-notifications@fortinet.com"

  runtime_python_lambda = "python3.10"

  upgrade_iam_role = "fsiem-upgrade-ssm-role-${var.environment}"
  setup_doc_name   = "fsiem_ingestion_setup_${var.environment}"

  log_persistance_days_long   = var.log_persistance_days_long[var.environment]
  log_persistance_days_medium = var.log_persistance_days_medium[var.environment]
  log_persistance_days_short  = var.log_persistance_days_short[var.environment]
}
