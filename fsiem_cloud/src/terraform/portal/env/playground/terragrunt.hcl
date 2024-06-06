include "root" {
  path = find_in_parent_folders()
}

inputs = {
  environment = "playground"
  # This is the ARN of the certificate that we manually import into AWS Cert Manager
  # This certificate is managed by Fortinet https://certificate-ra.fortinet.com/ system
  # For playground OM is responsible for getting/updating it.
  # Last updated 18-Dec-2023, will expire on January 14, 2025 and will require re-issue and re-import
  cert_arn                   = "arn:aws:acm:us-east-1:023941436530:certificate/07577d50-fd10-4f09-ab76-843225ff7119"
  domain_name                = "fortisiem-playground.forticloud.com"
  portal_api_build_zip       = "${get_parent_terragrunt_dir()}/../../portal/api/artifacts/lambda/fins-provisioning.zip"
  portal_ui_build_path       = "${get_parent_terragrunt_dir()}/../../portal/ui/artifacts/dist/fortisiem-portal-playground"
  fortimonitor_script        = "${get_parent_terragrunt_dir()}/../../python/fsiem_monitor/fsiem.py"
  fortimonitor_api_script    = "${get_parent_terragrunt_dir()}/../../python/fsiem_monitor/fsiem_api.py"
  notification_email_zip     = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_notification_email.zip"
  monitor_cleanup_zip        = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_monitor_cleanup.zip"
  ses_reject_zip             = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_ses_reject.zip"
  s3_tag_zip                 = "${get_parent_terragrunt_dir()}/../../python/artifacts/lambda_s3_tag.zip"
  layer_fsiem_api_client_zip = "${get_parent_terragrunt_dir()}/../../python/lambda_layer/artifacts/layer_fsiem_api_client.zip"
  aspnetcore_environment     = "Playground"
  saml_metadata              = "${get_terragrunt_dir()}/forticloud_saml.xml"

  # Required for ssm documents
   ssm_automation_src_dir    = "${get_parent_terragrunt_dir()}/../../python/lambda_ssm_automation/"
  ssm_automation_lambda_zip = "${get_parent_terragrunt_dir()}/../../python/artifacts/ssm_lambda.zip"


  slo_redirect_binding_uri = "https://customersso1-test.fortinet.com/saml-idp/z1qe88q10jgp490o/logout/"
  sso_redirect_binding_uri = "https://customersso1-test.fortinet.com/saml-idp/z1qe88q10jgp490o/login/"
  # Local development, Cloudfront and CNAME redirection
  callback_urls = [
    "https://localhost:4201/login",
    "https://d3f8tfq4jaelp9.cloudfront.net/login",
    "https://fortisiem-playground.forticloud.com/login"
  ]
  logout_urls = [
    "https://localhost:4201/logout",
    "https://localhost:4201/product-information",
    "https://d3f8tfq4jaelp9.cloudfront.net/logout",
    "https://d3f8tfq4jaelp9.cloudfront.net/product-information",
    "https://fortisiem-playground.forticloud.com/logout",
    "https://fortisiem-playground.forticloud.com/product-information"
  ]
  deployment_bucket        = "fsiem-terraform-ftn"
  deployment_bucket_region = "us-east-1"
}

terraform {
  # Having single slashes is important for deployment. Just ignore terraform warnings - it works. Trust me.
  # With two slashes, the deployment will fail to resolve paths, and an update will actually delete everything.
  # With 4 slashes, it will fail to create resources first time, but subsequent updates work fine.
  source = "../../"
}
