include "root" {
  path = find_in_parent_folders()
}

inputs = {
  environment             = "prod"
  workload_classification = "prod"

  # Portal web UI certificate, use RSA2048. Note RSA 4096 does NOT work.
  cert_arn = "arn:aws:acm:us-east-1:327332988639:certificate/8e13e0db-2ef9-462e-bd07-07ac1d9bc9df"

  # Portal web URL, excluding 'https://' prefix
  domain_name = "fortisiem.forticloud.com"

  # Build artifacts location for API and UI
  portal_api_build_zip = "${get_parent_terragrunt_dir()}/../../portal/api/artifacts/lambda/fins-provisioning.zip"
  portal_ui_build_path = "${get_parent_terragrunt_dir()}/../../portal/ui/artifacts/dist/fortisiem-portal-prod"

  # Custom python script for fortimonitor metrics gathering
  fortimonitor_script     = "${get_parent_terragrunt_dir()}/../../python/fsiem_monitor/fsiem.py"
  fortimonitor_api_script = "${get_parent_terragrunt_dir()}/../../python/fsiem_monitor/fsiem_api.py"


  # Built zip location for lambda functions
  notification_email_zip     = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_notification_email.zip"
  monitor_cleanup_zip        = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_monitor_cleanup.zip"
  ses_reject_zip             = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_ses_reject.zip"
  s3_tag_zip                 = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_s3_tag.zip"
  layer_fsiem_api_client_zip = "${get_parent_terragrunt_dir()}/../../python/lambda_layer/artifacts/layer_fsiem_api_client.zip"

  # Env var for API
  aspnetcore_environment = "Production"

  # File for Single Sign On (SSO)
  saml_metadata = "${get_terragrunt_dir()}/forticloud_saml.xml"

  # Required for ssm documents
   ssm_automation_src_dir    = "${get_parent_terragrunt_dir()}/../../python/lambda_ssm_automation/"
  ssm_automation_lambda_zip = "${get_parent_terragrunt_dir()}/../../python/artifacts/ssm_lambda.zip"

  # Process in the nutshell:
  # - Update fsiem_cognito_sp.xml
  # - Email to FortiCloud SSO team
  # - Receive back forticloud_saml.xml
  # - Update  fsiem_cognito_sp.xml, forticloud_saml.xml in git for every new environment
  # - Extract login and logout URLs from forticloud_saml.xml
  slo_redirect_binding_uri = "https://customersso1.fortinet.com/saml-idp/j6sj9b1pi235omug/logout/"
  sso_redirect_binding_uri = "https://customersso1.fortinet.com/saml-idp/j6sj9b1pi235omug/login/"

  # List of allowed URLs for SSO
  # Local development, Cloudfront and CNAME redirection
  callback_urls = [
    "https://d3e1wve916mgzw.cloudfront.net/login",
    "https://fortisiem.forticloud.com/login"
  ]
  logout_urls = [
    "https://d3e1wve916mgzw.cloudfront.net/logout",
    "https://d3e1wve916mgzw.cloudfront.net/product-information",
    "https://fortisiem.forticloud.com/logout",
    "https://fortisiem.forticloud.com/product-information"
  ]

  deployment_bucket        = "fsiem-terraform-prod"
  deployment_bucket_region = "us-east-1"
}

terraform {
  # Having single slashes is important for deployment. Just ignore terraform warnings.
  # It works. Trust me. With two slashes, the deployment will fail to resolve paths,
  # and an update will actually delete everything! With 4 slashes, it will fail to
  # create resources first time, but subsequent updates work fine.
  source = "../../"
}
