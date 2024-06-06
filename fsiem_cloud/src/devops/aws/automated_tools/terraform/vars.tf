data "aws_caller_identity" "current" {}

variable "lambda_runtime" { default = "python3.10" }

locals {
  account_id = data.aws_caller_identity.current.account_id
  global_tags = {
    Terraform              = "true"
    Environment            = "dev"
    WorkloadClassification = "dev"
    ProductName            = "FortiSIEM Cloud"
    SerialNumber           = "DEV_AUTOMATION"
  }
}
