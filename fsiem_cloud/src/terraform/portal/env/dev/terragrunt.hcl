include "root" {
  path = find_in_parent_folders()
}

inputs = {
  environment                = "dev"
  cert_arn                   = "arn:aws:acm:us-east-1:023941436530:certificate/8da8b571-76d7-4c44-9ad8-99e93fe81314"
  domain_name                = "fortisiem-dev.forticloud.com"
  portal_api_build_zip       = "${get_parent_terragrunt_dir()}/../../portal/api/artifacts/lambda/fins-provisioning.zip"
  portal_ui_build_path       = "${get_parent_terragrunt_dir()}/../../portal/ui/artifacts/dist/fortisiem-portal-dev"
  notification_email_zip     = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_notification_email.zip"
  monitor_cleanup_zip        = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_monitor_cleanup.zip"
  ses_reject_zip             = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_ses_reject.zip"
  s3_tag_zip                 = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_s3_tag.zip"
  layer_fsiem_api_client_zip = "${get_parent_terragrunt_dir()}/../../python/lambda_layer/artifacts/layer_fsiem_api_client.zip"

  # Custom python script for fortimonitor metrics gathering
  fortimonitor_script     = "${get_parent_terragrunt_dir()}/../../python/fsiem_monitor/fsiem.py"
  fortimonitor_api_script = "${get_parent_terragrunt_dir()}/../../python/fsiem_monitor/fsiem_api.py"


  # For dev, we have to use Staging, don't be a fool.
  # If you try using Development, like a sane person, you'd face this error:
  # "Set the DOTNET_USER_SECRETS_FALLBACK_DIR environment variable to a folder
  # where user secrets should be stored."
  aspnetcore_environment = "Staging"

  saml_metadata = "${get_terragrunt_dir()}/forticloud_saml.xml"

  # Required for ssm documents
  ssm_automation_src_dir    = "${get_parent_terragrunt_dir()}/../../python/lambda_ssm_automation/"
  ssm_automation_lambda_zip = "${get_parent_terragrunt_dir()}/../../python/artifacts/ssm_lambda.zip"

  slo_redirect_binding_uri = "https://customersso1-test.fortinet.com/saml-idp/6zpad3stzqamndv4/logout/"
  sso_redirect_binding_uri = "https://customersso1-test.fortinet.com/saml-idp/6zpad3stzqamndv4/login/"
  callback_urls = [
    "https://localhost:4201/login",
    "https://d4n5mreo88pq1.cloudfront.net/login",
    "https://fortisiem-dev.forticloud.com/login"
  ]
  logout_urls = [
    "https://localhost:4201/logout",
    "https://localhost:4201/product-information",
    "https://d4n5mreo88pq1.cloudfront.net/logout",
    "https://d4n5mreo88pq1.cloudfront.net/product-information",
    "https://fortisiem-dev.forticloud.com/logout",
    "https://fortisiem-dev.forticloud.com/product-information"
  ]
  deployment_bucket        = "fsiem-terraform-ftn"
  deployment_bucket_region = "us-east-1"
}

terraform {
  # Having single slashes is important for deployment. Just ignore terraform warnings.
  # The deployment will fail to resolve paths with 2 slashes, and an update will
  # actually delete everything. With 4 slashes, it will fail to create resources the
  # first time, but subsequent updates work fine.
  source = "../../"
}
