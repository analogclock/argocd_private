/*
  All variables are stored here
*/

#No of collector instances count
variable "data_collectors" { default = 0 }

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

variable "environment" { default = "playground" }
variable "region" { default = "us-east-1" }

variable "bm_serial_number" { default = "siemtest" }

variable "bm_region" {
  type = map(string)
  default = {
    "dev"        = "us-east-1"
    "playground" = "us-east-1"
    "prod"       = "us-east-1"
  }
}

variable "deployment_type" { default = "va" }

variable "collector_instance_types" {
  type    = list(string)
  default = ["c6i.xlarge", "c6a.xlarge", "c5.xlarge"]
}
variable "keeper_instance_types" {
  type    = list(string)
  default = ["c6i.xlarge", "c6a.xlarge", "c5.xlarge"]
}

# S3
# This S3 bucket contains scripts for VM configuration
variable "vm_bucket" { default = "fsiem-terraform" }

variable "primary_az" { default = "" }



locals {
  global_tags = {
    Terraform              = "true"
    Environment            = var.environment
    WorkloadClassification = var.workload_classification
    ProductName            = "FortiSIEM Cloud"
    SerialNumber           = var.bm_serial_number
  }

  session_manager_bucket_arn = "arn:aws:s3:::fsiem-session-manager-logs-${var.environment}"

  # e.g. fsiem-terraform-dev-scripts
  s3_scripts_bucket     = "${var.vm_bucket}-${var.environment}-scripts"
  s3_scripts_bucket_arn = "arn:aws:s3:::${local.s3_scripts_bucket}"


  # EBS disk timeout values defaults
  # used for all EBS actions, defaults are normally
  # 5 minutes which in most cases is too short
  create_timeout = "15m"
  update_timeout = "15m"
  delete_timeout = "30m"


  # if we are using CH then we choose 1 primary az (this comes in via Provisioning API)
  # else choose the first one from the list of availability zones in that aws region
  primary_availability_zone = var.primary_az == "" ? [data.aws_availability_zones.available.names[0]] : [var.primary_az]

}
