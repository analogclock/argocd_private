include {
  path = "..//..//terragrunt.hcl"
}

remote_state {
  backend = "local"
  config = {
    path = "${get_parent_terragrunt_dir()}/${path_relative_to_include()}/terraform.tfstate"
  }

  generate = {
    path = "backend.tf"
    if_exists = "overwrite"
  }
}

inputs = {
  region = "us-east-1"
  environment = "playground"
  serial_number = "plan-test"
  has_nfw = true
}

terraform {
  source = "${path_relative_from_include()}//ec2"
}

locals {
  dynamodb_table = "fsiem_activation_table_playground"
}
