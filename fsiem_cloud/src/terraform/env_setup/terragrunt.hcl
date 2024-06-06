# Env setup parent terragrunt file.

# This is used to override locals via children .hcl
# Based on https: //sandeeplamba.dev/terragrunt-remote_state/
locals {
  # Default parent values, state location in S3 and locks in DynamoDb
  s3_region      = "eu-west-1"
  s3_bucket      = "fsiem-terraform"
  dynamodb_table = "tf_state_lock_playground"

  # Overrides/merge
  needs_merge    = fileexists(local.overrides_path)
  overrides_path = "${get_terragrunt_dir()}/terragrunt.var.overrides.yaml"
  overrides      = yamldecode(local.needs_merge ? file(local.overrides_path) : "{}")
  overridden     = local.needs_merge ? merge(local.overrides.tg_remote_state) : {}
}

# Retry on an error, see https://terragrunt.gruntwork.io/docs/features/auto-retry/
retryable_errors         = ["(?s).*"]
retry_max_attempts       = 3
retry_sleep_interval_sec = 5

remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket         = local.needs_merge ? local.overridden.s3_bucket : local.s3_bucket
    key            = "env_setup/${path_relative_to_include()}/terraform.tfstate"
    region         = local.needs_merge ? local.overridden.s3_region : local.s3_region
    dynamodb_table = local.needs_merge ? local.overridden.dynamodb_table : local.dynamodb_table
    encrypt        = true
  }
}
