/*
  All variables are stored here. Override them via .hcl file.
*/

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
    "af-south-1",
    "ap-east-1"
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


variable "deployment_bucket" {
  default = "fsiem-terraform"
}

locals {
  waf_super_name = "waf-super-${var.environment}"

  # Includes required infosec tags as listed in this doc:
  # https://fuse.fortinet.com/HigherLogic/System/DownloadDocumentFile.ashx?DocumentFileKey=051af8f5-6198-cfdd-0a14-4a133fb267a3&forceDialog=0
  global_tags = {
    Terraform              = "true"
    Environment            = var.environment
    WorkloadClassification = var.workload_classification
    ProductName            = "FortiSIEM Cloud"
    SerialNumber           = "env_setup"
  }
}
