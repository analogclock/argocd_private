/*
  User pool clients, there are two here:
  1. The main forticloud pool client, the UI uses this to trigger SSO redirects etc
  2. The license client, which generates a secret and is used to get license files for deployments
*/
resource "aws_cognito_user_pool_client" "forticloud" {
  user_pool_id = aws_cognito_user_pool.forticloud.id

  name                  = "forticloud"
  access_token_validity = 15
  allowed_oauth_flows = [
    "code"
  ]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "phone",
    "profile"
  ]
  callback_urls           = var.callback_urls
  enable_token_revocation = false
  explicit_auth_flows = [
    "ALLOW_CUSTOM_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]
  generate_secret               = null
  id_token_validity             = 15
  logout_urls                   = var.logout_urls
  prevent_user_existence_errors = "LEGACY"
  read_attributes = [
    "address",
    "birthdate",
    "custom:IAM_account_alias",
    "custom:IAM_account_name",
    "custom:IAM_username",
    "custom:NameId",
    "custom:auth_status",
    "email",
    "email_verified",
    "family_name",
    "gender",
    "given_name",
    "locale",
    "middle_name",
    "name",
    "nickname",
    "phone_number",
    "phone_number_verified",
    "picture",
    "preferred_username",
    "profile",
    "updated_at",
    "website",
    "zoneinfo"
  ]
  refresh_token_validity = 1
  supported_identity_providers = [
    aws_cognito_identity_provider.forticloud.provider_name
  ]
  write_attributes = [
    "address",
    "birthdate",
    "custom:IAM_account_alias",
    "custom:IAM_account_name",
    "custom:IAM_username",
    "custom:NameId",
    "custom:auth_status",
    "email",
    "family_name",
    "gender",
    "given_name",
    "locale",
    "middle_name",
    "name",
    "nickname",
    "phone_number",
    "picture",
    "preferred_username",
    "profile",
    "updated_at",
    "website",
    "zoneinfo"
  ]
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }
}

resource "aws_cognito_user_pool_client" "licence_activation" {
  user_pool_id = aws_cognito_user_pool.forticloud.id

  name                  = "licence_activation"
  access_token_validity = 60
  allowed_oauth_flows = [
    "client_credentials"
  ]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes = [
    "licence/licence.get"
  ]
  callback_urls           = []
  enable_token_revocation = false
  explicit_auth_flows     = []
  generate_secret         = true
  id_token_validity       = 60
  logout_urls             = []
  read_attributes = [
    "email",
    "email_verified"
  ]
  refresh_token_validity       = 30
  supported_identity_providers = []
  write_attributes = [
    "email"
  ]
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }
}

resource "aws_cognito_user_pool_client" "status_update" {
  user_pool_id = aws_cognito_user_pool.forticloud.id

  name                  = "status_update"
  access_token_validity = 60
  allowed_oauth_flows = [
    "client_credentials"
  ]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes = [
    "status/update.post"
  ]
  callback_urls           = []
  enable_token_revocation = false
  explicit_auth_flows     = []
  generate_secret         = true
  id_token_validity       = 60
  logout_urls             = []
  read_attributes = [
    "email",
    "email_verified"
  ]
  refresh_token_validity       = 30
  supported_identity_providers = []
  write_attributes = [
    "email"
  ]
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }
}
