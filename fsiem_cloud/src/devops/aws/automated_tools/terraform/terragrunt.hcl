remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket         = "fsiem-terraform-ftn"
    key            = "devops_automation_tools/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
  }
}
