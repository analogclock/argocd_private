# Retry on an error, see https://terragrunt.gruntwork.io/docs/features/auto-retry/
retryable_errors         = ["(?s).*"]
retry_max_attempts       = 3
retry_sleep_interval_sec = 5

# Terragrunt before and after hooks allow custom actions before and after the execution of a terraform command
# https://terragrunt.gruntwork.io/docs/features/before-and-after-hooks/
# Currently these are used to update our DynamoDB table with the status of the deployment.
# The initial status Initializing is created by the portal API, while these hooks add the status CreateInProgress and Complete.
# When the deployment is destroyed it also deletes the item from DynamoDB to allow it to be rebuilt.
terraform {

  # Create new deployment
  before_hook "create_before_hook" {
    commands = ["apply"]
    execute  = ["bash", "../hooks/set_status.sh", "CreateInProgress"]
  }
  after_hook "create_after_hook" {
    commands = ["apply"]
    execute  = ["bash", "../hooks/set_status_and_vars.sh", "${get_terragrunt_dir()}", "LicenseInProgress"]
  }
  error_hook "create_error_hook" {
    commands  = ["apply"]
    execute   = ["bash", "../hooks/set_status.sh", "CreateFailed"]
    on_errors = [".*"]
  }

  # Update existing deployment
  # Expecting UPDATING_DEPLOYMENT env var set to true to run the scripts
  before_hook "update_before_hook" {
    commands = ["apply"]
    execute  = get_env("UPDATING_DEPLOYMENT", "false") == "false" ? ["echo", "This is not an update, exiting the hook"] : ["bash", "../hooks/set_status.sh", "UpdateInProgress"]
  }
  after_hook "update_after_hook" {
    commands = ["apply"]
    execute  = get_env("UPDATING_DEPLOYMENT", "false") == "false" ? ["echo", "This is not an update, exiting the hook"] : ["bash", "../hooks/set_status_and_vars.sh", "${get_terragrunt_dir()}", "UpdateCompleted"]
  }
  error_hook "update_error_hook" {
    commands  = ["apply"]
    execute   = get_env("UPDATING_DEPLOYMENT", "false") == "false" ? ["echo", "This is not an update, exiting the hook"] : ["bash", "../hooks/set_status.sh", "UpdateFailed"]
    on_errors = [".*"]
  }

  # Delete deployment
  before_hook "destroy_before_hook" {
    commands = ["destroy"]
    execute  = ["bash", "../hooks/set_status.sh", "DeleteInProgress"]
  }
  # Clear S3 folders after stack was removed.
  # NOTE: do this _after_ the stack is gone otherwise clickhouse will try
  # re-uploading some data while the stack is being deleted
  after_hook "destroy_before_hook_clear_s3" {
    commands = ["destroy"]
    execute  = ["bash", "../hooks/delete_from_clickhouse.sh"]
  }
  after_hook "destroy_after_hook" {
    commands = ["destroy"]
    execute  = ["bash", "../hooks/destroy_after.sh"]
  }
  error_hook "destroy_error_hook" {
    commands  = ["destroy"]
    execute   = ["bash", "../hooks/set_status.sh", "DeleteFailed"]
    on_errors = [".*"]
  }
}
