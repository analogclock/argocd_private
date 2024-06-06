#
# Creates Cognito resources to allow access from AWS into Fsiem VM API
#
resource "aws_cognito_resource_server" "appserver_cloud_automation" {
  user_pool_id = aws_cognito_user_pool.forticloud.id

  identifier = "appserver"
  name       = "appserver_fsiem_cloud"

  # Creates a scope that looks like 'appserver/cloud_automation'
  scope {
    scope_name        = "cloud_automation"
    scope_description = "Allow operations for SaaS cloud automation inside the VMs"
  }
}

resource "aws_cognito_user_pool_client" "fsiem_vm_auth_pool_client" {
  name                   = "fsiem-vm-auth-pool-client-${var.environment}"
  user_pool_id           = aws_cognito_user_pool.forticloud.id
  access_token_validity  = 60
  id_token_validity      = 60
  refresh_token_validity = 30
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }
  allowed_oauth_flows_user_pool_client = true
  enable_token_revocation              = false
  generate_secret                      = true
  allowed_oauth_flows                  = ["client_credentials"]
  # If this fails with scope does not exist - run it twice
  allowed_oauth_scopes         = ["appserver/cloud_automation"]
  callback_urls                = []
  explicit_auth_flows          = []
  logout_urls                  = []
  supported_identity_providers = []
  read_attributes              = ["email", "email_verified"]
  write_attributes             = ["email"]
}
