/*
  Identity provider to support SP and IDP request/responses
  IDP here is FortiCloud SSO
  SP is our identity provider
  When successful the Provider will provide an Auth Token
  to allow access to other resources (Portal API)
*/

resource "aws_cognito_identity_provider" "forticloud" {
  user_pool_id  = aws_cognito_user_pool.forticloud.id
  provider_name = "FortiCloud"
  provider_type = "SAML"

  provider_details = {
    MetadataFile          = file(var.saml_metadata)
    IDPSignout            = true
    SLORedirectBindingURI = var.slo_redirect_binding_uri
    SSORedirectBindingURI = var.sso_redirect_binding_uri
  }

  # map specific attributes that come from the IDP response
  # this makes them available on the Authentication Token
  attribute_mapping = {
    "custom:IAM_account_alias" = "IAM_account_alias"
    "custom:IAM_account_name"  = "IAM_account_name"
    "custom:IAM_username"      = "IAM_username"
    "custom:NameId"            = "NameID"
    "custom:auth_status"       = "Authentication_status"
  }
}
