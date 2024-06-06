/*
  All variables are stored here. Override them via .hcl file.
*/
variable "region" {
  default = "us-east-1"
}

variable "additional_regions" {
  description = "Other regions FSIEM can be deployed to"
  default = [
    "eu-central-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "eu-north-1",
    "us-east-2",
    "us-west-2",
    "ca-central-1",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "me-south-1",
    "ap-east-1",
    "af-south-1"
  ]
}

variable "environment" {
  default = "dev"
}

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
    error_message = "Workload classification must match one of the valid labels."
  }
}

# A valid cert must already have been uploaded to AWS certificate manager in the specified region.
# Use internal Fortinet systems to request a new cert and manually import it into AWS cert manager.
# This cert must be issued via Fortinet, so that Fortinet's SSO works fine, we cannot use AWS
variable "cert_arn" {
  default = "arn:aws:acm:us-east-1:023941436530:certificate/5e596fb4-9d6a-4f4a-9e15-6b69b499e47d"
}

variable "domain_name" {
  default = "fortisiem-dev.forticloud.com"
}

variable "hosted_zone_name" {
  type = map(string)
  default = {
    "dev"        = "dev.fortisiem.cloud"
    "playground" = "playground.fortisiem.cloud"
    "prod"       = "fortisiem.cloud"
  }
}

variable "portal_ui_build_path" {
  default = "../../portal/ui/artifacts/dist/fortisiem-portal-dev"
  validation {
    condition     = fileexists("${var.portal_ui_build_path}/index.html")
    error_message = "The file index.html does not exist in UI artifacts dir."
  }
}

variable "portal_api_build_zip" {
  default = "../../portal/api/artifacts/lambda/fins-provisioning.zip"
  validation {
    condition     = fileexists(var.portal_api_build_zip)
    error_message = "The file fins-provisioning.zip does not exist in API artifacts dir."
  }
}

variable "fortimonitor_script" {
  default = "../../python/fsiem_monitor/fsiem.py"
  validation {
    condition     = fileexists(var.fortimonitor_script)
    error_message = "The file fsiem.py does not exist in the fsiem_monitor dir."
  }
}

variable "fortimonitor_api_script" {
  default = "../../python/fsiem_monitor/fsiem_api.py"
  validation {
    condition     = fileexists(var.fortimonitor_api_script)
    error_message = "The file fsiem_api.py does not exist in the fsiem_monitor dir."
  }
}

variable "notification_email_zip" {
  default = "../../python/artifacts/lambda_notification_email.zip"
  validation {
    condition     = fileexists(var.notification_email_zip)
    error_message = "The file lambda_notification_email.zip does not exist in artifacts dir."
  }
}

variable "monitor_cleanup_zip" {
  default = "../../python/artifacts/lambda_monitor_cleanup.zip"
  validation {
    condition     = fileexists(var.monitor_cleanup_zip)
    error_message = "The file lambda_monitor_cleanup.zip does not exist in artifacts dir."
  }
}

variable "ses_reject_zip" {
  default = "../../python/artifacts/lambda_ses_reject.zip"
  validation {
    condition     = fileexists(var.ses_reject_zip)
    error_message = "The file lambda_ses_reject.zip does not exist in artifacts dir."
  }
}

variable "s3_tag_zip" {
  default = "../../python/artifacts/lambda_s3_tag.zip"
  validation {
    condition     = fileexists(var.s3_tag_zip)
    error_message = "The file lambda_s3_tag.zip does not exist in artifacts dir."
  }
}

variable "layer_fsiem_api_client_zip" {
  default = "../../python/artifacts/layer_fsiem_api_client.zip"
  validation {
    condition     = fileexists(var.layer_fsiem_api_client_zip)
    error_message = "The file layer_fsiem_api_client.zip does not exist in artifacts dir."
  }
}

variable "aspnetcore_environment" {
  default = "Staging"
}

variable "saml_metadata" {
  default = "./env/dev/forticloud_saml.xml"
  validation {
    condition     = fileexists(var.saml_metadata)
    error_message = "The file forticloud_saml.xml does not exist in the expected path."
  }
}

variable "ssm_automation_src_dir" {
  default = "../../python/lambda_ssm_automation/"
}

variable "ssm_automation_lambda_zip" {
  default = "../../python/artifacts/ssm_lambda.zip"
}

# SLO and SSO URIs are coming from src/terraform/portal/env/<env_name>/forticloud_saml.xml file.
# You will get new URIs for every new environment. These are provided by FortiCloud SSO team.
variable "slo_redirect_binding_uri" {
  default = "https://customersso1-test.fortinet.com/saml-idp/6zpad3stzqamndv4/logout/"
}

variable "sso_redirect_binding_uri" {
  default = "https://customersso1-test.fortinet.com/saml-idp/6zpad3stzqamndv4/login/"
}

variable "callback_urls" {
  type = list(string)
  default = [
    "https://localhost:4201/login",                # Local development redirection
    "https://d2ie84howhzx4e.cloudfront.net/login", # Cloudfront redirection
    "https://fortisiem-dev.forticloud.com/login"   # CNAME redirection
  ]
}

variable "logout_urls" {
  type = list(string)
  default = [
    "https://localhost:4201/logout",
    "https://localhost:4201/product-information",
    "https://d2ie84howhzx4e.cloudfront.net/logout",
    "https://d2ie84howhzx4e.cloudfront.net/product-information",
    "https://fortisiem-dev.forticloud.com/logout",
    "https://fortisiem-dev.forticloud.com/product-information"
  ]
}

variable "deployment_bucket" {
  default = "fsiem-terraform"
}

variable "deployment_bucket_region" {
  default = "eu-west-1"
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
  account_id                        = data.aws_caller_identity.current.account_id
  gateway_name                      = "${var.environment}-infrastructure-provisioning-web-api"
  fortinet_one_certificate_key      = "provisioning-${var.environment}/f1/certificate"
  fortinet_one_passphrase_key       = "provisioning-${var.environment}/f1/passphrase"
  licensing_certificate_key         = "provisioning-${var.environment}/licensing/certificate"
  licensing_passphrase_key          = "provisioning-${var.environment}/licensing/passphrase"
  fortimonitor_api_key              = "fortimonitor-api-key-${var.environment}"
  fortimonitor_api_key_write        = "fortimonitor-api-key-write-${var.environment}"
  s3_scripts_bucket                 = "fsiem-terraform-${var.environment}-scripts"
  s3_taclogs_bucket                 = "fsiem-terraform-${var.environment}-taclogs"
  s3_upgrade_packages_bucket        = "fsiem-${var.environment}-upgrade-packages"
  dynamodb_backup_table             = "fsiem_clickhouse_backup_${var.environment}"
  dynamodb_backup_options_table     = "fsiem_backup_options_${var.environment}"
  dynamodb_restore_table            = "fsiem_clickhouse_restore_${var.environment}"
  dynamodb_activation_table         = "fsiem_activation_table_${var.environment}"
  dynamodb_upgrades_table           = "fsiem_upgrades_table_${var.environment}"
  dynamodb_scheduled_upgrades_table = "fsiem_scheduled_upgrades_table_${var.environment}"
  dynamodb_poc_approval_table       = "fsiem_poc_approval_table_${var.environment}"
  dynamodb_storage_approval_table   = "fsiem_storage_approval_table_${var.environment}"
  dynamodb_email_block_table        = "fsiem_email_block_${var.environment}"
  dynamodb_compute_override_table   = "fsiem_compute_override_${var.environment}"
  dynamodb_ext_storage_table        = "fsiem_external_storage_table_${var.environment}"
  dynamodb_ext_storage_status_table = "fsiem_external_storage_status_table_${var.environment}"
  dynamodb_metrics_storage_table    = "fsiem_metrics_storage_${var.environment}"
  waf_cloudfront_name               = "waf_cloudfront_${var.environment}"
  waf_api_name                      = "waf_api_${var.environment}"
  waf_super_name                    = "waf_super_${var.environment}"
  ssm_automation_lg                 = "ssm_automation_${var.environment}"

  is_dev_or_playground = var.environment == "dev" || var.environment == "playground" ? true : false

  # Includes required infosec tags as listed in this doc:
  # https://fuse.fortinet.com/HigherLogic/System/DownloadDocumentFile.ashx?DocumentFileKey=051af8f5-6198-cfdd-0a14-4a133fb267a3&forceDialog=0
  global_tags = {
    Terraform              = "true"
    Environment            = var.environment
    WorkloadClassification = var.workload_classification
    ProductName            = "FortiSIEM Cloud"
    SerialNumber           = "Portal"
  }

  notification_email = "fortisiem-cloud-notifications@fortinet.com"
  teams_email        = "f71b3906.fortinet.onmicrosoft.com@amer.teams.ms"

  clickhouse_archive_data_prefix = "fsiem-clickhouse-data"
  clickhouse_backup_prefix       = "fsiem-clickhouse-backups"
  runtime_python_lambda          = "python3.11"

  lambda_s3_tag_name  = "function:fsiem_s3_tag_${var.environment}"
  lambda_s3_tag_arn   = "arn:aws:lambda:${var.region}:${local.account_id}:${local.lambda_s3_tag_name}"
  s3_job_bucket_name  = "fsiem-s3-job-${var.environment}"
  s3_tagging_role_arn = "arn:aws:iam::${local.account_id}:role/lambda-fsiem-s3-tag-${var.environment}"

  # Email addresses for FortiSIEM cloud team, use this for TO and FROM email addresses
  email_from_addr = "noreply@${aws_ses_domain_mail_from.fortisiem_cloud.mail_from_domain}"
  email_to_addr   = "fortisiem-cloud-notifications@fortinet.com"

  log_persistance_days_long   = var.log_persistance_days_long[var.environment]
  log_persistance_days_medium = var.log_persistance_days_medium[var.environment]
  log_persistance_days_short  = var.log_persistance_days_short[var.environment]
}
