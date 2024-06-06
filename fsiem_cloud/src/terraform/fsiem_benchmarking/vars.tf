/*
  All variables are stored here
*/
#Required number of collectors for the test
variable "data_collectors" { default = 0 }

variable "log_persistance_days_long" { default = 30 }
variable "log_persistance_days_medium" { default = 14 }
variable "log_persistance_days_short" { default = 7 }


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

variable "serial_number" { default = "siemtestcoll" }

# S3
# This S3 bucket contains scripts for VM configuration
variable "vm_bucket" { default = "fsiem-terraform" }

locals {
  global_tags = {
    Terraform              = "true"
    Environment            = var.environment
    WorkloadClassification = var.workload_classification
    ProductName            = "FortiSIEM Cloud"
    SerialNumber           = var.serial_number
  }

}
